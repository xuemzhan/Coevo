# Coevo 代码审查（CODE_REVIEW）

> 审查范围：`src/coevo/`（11 子包、48 个 .py 文件）+ 配套 `tests/`（unit 310、integration 133、security 90+1 fail、e2e 3 → 全部通过 pytest 实测）。
> 审查方式：实测 quality gate + 逐文件人工审查；bug/鲁棒性/优化分类用 measured numbers 标注，不引用未执行的文档百分比。
> 审查日期：2026-07-30（HEAD `ec7f9bc` / 上一提交 `4a6d12d`；US-13-AC-1 已工作但未提交）。

---

## 0. 实测数据（不是文档宣称）

| 项目 | 命令 | 结果 |
|---|---|---|
| Unit | `pytest tests/unit -q` | **310 passed, 1 skipped, 148 subtests passed in 32.28s** |
| Integration | `pytest tests/integration -q` | **133 passed, 28 subtests passed in 73.50s** |
| Security | `pytest tests/security -q` | **90 passed, 14 subtests passed, 1 FAILED in 163.82s** |
| E2E | `pytest tests/e2e -q` | **3 passed in 64.47s** |
| 源码规模 | `find src/coevo -name __pycache__ -prune -o -name '*.py' -print \| xargs wc -l` | **~235 KB, 48 .py**（其中 `merge/__init__.py` 1188 行、`decision_brief/__init__.py` 1414 行） |
| 已完成 AC | `loop/BACKLOG.yaml` | **13 个 user-story (US-0/US-1/US-2/US-3/US-5/US-6/US-9/US-10/US-11/US-12/US-13) 全部 status=done**；US-4/US-7/US-8/US-14/US-15 status=ready/待办 |
| 当前循环 | `loop/STATE.json` | iteration=13, current_story=US-13, status=done, failed_verifications=0 |

### 0.1 实测发现的 1 个 fail（不是"全绿"）

`tests/security/test_audit_seal.py::AuditSealTests::test_current_project_audit_is_fully_sealed`

```
AssertionError: 'fully-sealed' != 'valid-prefix-with-unsealed-tail'
```

根因：跑测试 → audit log 追加了 1 行（head=527, 当前=528+）→ `verify_seal()` 看到签名头与文件不一致。重新跑 `make_quality_gate` 重新封签会恢复 fully-sealed。这暴露了 **测试不可重入**：跑任何 `pytest` 后都会立刻把 `verify_seal` 测成 fail。属于"测试顺序副作用"问题，应归类为"鲁棒性 / 优化"项（见 §4.1）。

---

## 1. 一句话总评

> 整体质量高、约束设计认真（fail-closed / 不可重入 / 不可子类化 / 路径越权检查 / 私钥不出 Windows CNG），但出现 **1 个高优先级真 bug、3 个明显代码坏味、6 个鲁棒性弱化点**，都是 1-2 小时内可修的小问题。

| 维度 | 评分 | 依据 |
|---|---|---|
| 正确性（已测） | **7/10** | 1 真 bug + 1 fail-closed-but-useless 段（§3.1, §3.2） |
| 鲁棒性 | **7/10** | §4.1 测试副作用、§4.2 sub 子类封印、§4.4 path 分割、§4.5 时间字符串 |
| 可维护性 | **8/10** | docstring 极全 + §5.1 / §5.2 拆 API + dataclass(frozen=True) 一致 |
| 性能 | **8/10** | 全部纯函数 + 链表式不可变；热路径都是 O(n)；§5.5 merge O(n²) |
| 协议契合 | **9/10** | wire layout 严格 + canonical JSON 严格 + fail-closed 完整 |
| 安全 | **9/10** | 私钥只进 CNG + 审计链 + cert 路径校验；§6.1 一处 DAO 静默吞异常 |

---

## 2. 模块/包结构总览

```
src/coevo/
├── identity/      US-0       private_keys + audit_anchor + repository(7 文件)
├── task_flow/     US-1       parser + service + mapping + models(5 文件)
├── task_decomposition/ US-2  baseline + dependency_graph + models + service(5 文件)
├── talent/        US-3       recommender + redaction + models + service(5 文件)
├── protocol/      US-5       agent_package + sm2_sign + sm2_keywrap + agent_payload
│                             + package_builder + import_transaction
│                             + processed_package_store + import_service + replay_detector
│                             + sm2_extension(11 文件)
├── workspace/     US-6       paths + init_service + models(4 文件)
├── report/        US-9       builder + models(3 文件)
├── merge/         US-10      __init__(1188) + receipt + repository(3 文件)
├── risk/          US-11      __init__(506) 单文件巨型模块
├── supervision/   US-12      __init__(631) 单文件巨型模块
└── decision_brief/ US-13     __init__(1414) 单文件巨型模块  ← 最新, 未追踪
```

**关注点**：US-11/12/13 三个最新模块都用单文件 `__init__.py` 巨型化（500-1400 行），与 US-10 的多文件拆分风格不一致。

---

## 3. 真 bug 清单（应当修复）

### 3.1 [BUG-P1] `build_signed_payload` 永远不会签名，文档自相矛盾

`src/coevo/protocol/package_builder.py:280-297`

```python
def build_signed_payload(manifest, *, signer_cert_id, signed_at=None) -> SignatureRecord:
    from .sm2_sign import AgentPackageCryptoUnavailableError
    raise AgentPackageCryptoUnavailableError(
        "sign_manifest is awaiting an approved SM2 product"
    )
```

**问题**：
1. 函数接受 `manifest` / `signer_cert_id` / `signed_at` 三个参数但**全部未使用** —— 直接 raise。
2. `signed_at` 是 default `None`，但函数名暗示它会签出带时间的记录。
3. `manifest` 参数没用，会让 caller 误以为"我传了 manifest 就得到了它的签名记录"。
4. 文档说"`The wire format is final`"，但实际上该函数根本不返回 `SignatureRecord`；调用方拿不到任何东西。

**修法**：把 `build_signed_payload` 改成"build + verify + return SignatureRecord"模板（和 `package_builder.build_unsigned_package` 同样的接口形状），内部 raise 而不是哑 raise。或者改名为 `assert_signed_payload_blocked` 并删除签名参数。

**风险**：下游模块（如果有）若 await 该函数的返回值会拿到一个 raise；当前所有调用方要么不调用，要么已被测试覆盖成 raise。

### 3.2 [BUG-P1] US-9 ReportBuilder 接受 `base_revision` 校验后 `pass` 跳过

`src/coevo/report/builder.py:163-172`

```python
if manifest.base_revision != baseline.process_flow_ref[0]:
    # ... 注释解释 baseline.process_flow_ref 是 (unit_id, version)
    pass  # accept — the report's base_revision is itself the canonical id
```

**问题**：
1. **校验名是"AC-3"（注释里写的），但实际不校验**。
2. `baseline.process_flow_ref[0]` 是 unit_id（来自 US-1 流程），**不包含**项目基线版本；US-9 AC-3 实际要求"report base_revision == baseline's project master revision"。
3. 当前实现等于 AC-3 fail-open：任意 base_revision 都被接受，违反 docstring "AC-3: baseline and manifest must agree on project_id and base_revision. Reject otherwise (fail-closed)."

**修法**：把校验改成 `manifest.base_revision == _master_revision(baseline.project_id, baseline.version)`，不匹配则 `raise ReportManifestValidationError(...)`。可以 import `_master_revision` from `merge.__init__`（public enough）或者复制格式常量。

**影响**：可能影响测试 `tests/unit/test_report_builder.py` —— 如果有测试故意触发 mismatch 路径需要对应更新。

### 3.3 [BUG-P2] `PackageImportService.import_package` 提前 return 但 `import datetime` 在函数末尾

`src/coevo/protocol/import_service.py:151-156, 180-181`

```python
try:
    tx = self.importer.advance(tx, to_step=ImportStep.DECRYPT_AND_INSPECT)
    # Caller-side validation: fixed-header consistency
    if package.fixed_header.header_length != len(_payload_blob(package)):
        # placeholder — actual length is computed by to_bytes()
        pass    # ← 应 raise
    tx = self.importer.advance(tx, to_step=ImportStep.PREPARE_WORKSPACE)
    ...
```

**问题**：
1. `if` 分支是 `pass`，意味着 **length 不一致时仍继续走完整 7 步**。这是占位代码，但被遗忘在线上分支里。
2. 同时下面 `_now_utc_iso_z()` 内 `import datetime as dt` 是函数内 import；建议顶层 import。
3. `_payload_blob(package) == package.to_bytes()`，每次校验都重新 serialize 整个包（~10 KB），O(n) 额外开销；可以做单次缓存。

**修法**：把 `pass` 改成 `raise AgentPackageImportValidationError("fixed header length mismatch")`，或干脆删掉这段（`BuiltPackage.to_bytes()` 已经在 `BuiltPackage` 构造时隐式一致）。`_now_utc_iso_z` 顶层化 import。

### 3.4 [BUG-P2] `MergeEngine._reject` 静默吞 `AttributeError` 决定 decision_maker

`src/coevo/merge/__init__.py:1011-1020`

```python
try:
    dm = import_outcome.record.package.recipient_cert_id
except Exception:
    dm = ""
```

**问题**：`except Exception` 太宽 — 静默吞掉所有错误（包括 `AttributeError` / `MemoryError` / `KeyboardInterrupt` 之外），将 `dm` 设为空串而不是显式 `raise`。攻击者如果在 `import_outcome` 路径中塞入畸形对象，可能导致 `decision_maker` 为空串（实际上后续 record 仍然会被构建，只是 `decision_maker=""`）。

**修法**：只 catch `(AttributeError, TypeError)`，其余 re-raise；`dm=""` 仅在 `record` 字段缺失时为合法。

---

## 4. 鲁棒性弱化点（应当修复或加测试）

### 4.1 [ROB-1] Security test 不可重入（已实测 fail）

实测：先 `pytest tests/unit` → `tool-audit.jsonl` 追加 1 行 → `tests/security/test_audit_seal.py::test_current_project_audit_is_fully_sealed` 立即 fail，因为 head signature 在 527 行而文件已经 528+。

**根因**：`verify_seal()` 看到任何 unsealed tail 都返回 `valid-prefix-with-unsealed-tail`（设计如此，是好功能），但 `pytest` 自身在测试运行时 append 了 `tool-audit.jsonl` 一行（用 `_record_audit` 之类），所以测试不可重入。

**修法**（任选一）：
- A. 改 `verify_seal()` 在测试模式下接受临时 mock：让 `test_audit_seal.py` 在 setup 时把 `tool-audit.jsonl` 备份 / 截断。
- B. `pytest.ini` 加 `-p no:cacheprovider --no-header` 之外的副作用屏蔽（已加，但只屏蔽 cache）。
- C. 把 `tests/security/test_audit_seal.py` 标记为 `@pytest.mark.last` 并在 conftest hook 里跳过副作用 append。

实测显示 `make_quality_gate` 自身会自动 re-seal（这是 `loop/STATE.json` 注释里说的"re-seal on every run is expected"），所以"可重入"在生产中不存在问题，只是 **CI gate 实测会 fail**。建议 CI 在跑 `test_audit_seal` 之前先跑一次 re-seal。

### 4.2 [ROB-2] `MergeCommitReceiptStore.__init_subclass__` 拒绝子类，但 `__init__` 仍可被 fake

`src/coevo/merge/receipt.py:252-257`

```python
def __init_subclass__(cls, **kwargs):
    raise TypeError("MergeCommitReceiptStore may not be subclassed")

def __init__(self, receipts=(), *, _seal=None) -> None:
    if _seal is not _STORE_SEAL or type(receipts) is not tuple:
        raise MergeCommitReceiptError("receipt store construction is sealed")
```

**问题**：
1. `_STORE_SEAL` 是 module-level `object()`，**任何能 import 该 module 的代码**都可以传 `_seal=_STORE_SEAL` 绕过。
2. 真正的"密封"应该用 `__new__` + `_seal` 作为位置参数而不是 keyword，且通过闭包或工厂类封装。
3. 当前实现 = "约定密封"（import 私有 sentinel）→ 攻击者控制环境即绕过。

**修法**：将 `__init__` 私有化（`_MergeCommitReceiptStoreInit.__init__`），把构造走 `MergeCommitReceiptStore.empty()` / `append_signed_receipt` 两个唯一公开入口。或者用 `__new__` 在创建时检查栈帧，拒绝非 factory 调用。

**严重性**：中。模块没有 IO，主要被 service 调用；但若 US-14 / US-15 引入"外部 audit loader"，这个密封会被绕过。

### 4.3 [ROB-3] `FieldMerge` 反复 `tuple(set(...))` 不去重排序的不变量

`src/coevo/merge/__init__.py:1064-1087` (`_merge_text_field`)

```python
return FieldMerge(
    field_path=field_path,
    original_value=MISSING,
    current_value=current_value if current_value is not None else MISSING,
    ...
)
```

**问题**：
1. `current_value` 类型未做约束 — 可以传任意对象（list / dict / 自定义类），下游 `to_dict()` 用 `if isinstance(value, enum.Enum)` 处理枚举，但 **list / dict 会原样塞进 JSON 序列化**，可能产生非确定性结果（dict key 顺序）或循环引用。
2. 整段 per-field helper (`_merge_text_field`, `_merge_status_field`, `_merge_str_list_field`) 大量重复 — 三个方法形同复制粘贴，仅 decision path 略不同。

**修法**：在 `FieldMerge.__post_init__` 里给 `current_value` / `submitted_value` 加类型白名单（str / int / float / bool / None / MISSING / 已知 dataclass / tuple of these）。把三个 helper 合并成一个 `_merge_simple_field(..., decision_fn, allow_list=...)`。

### 4.4 [ROB-4] `WorkspacePath` 用 `/` 分割校验，Windows 路径会被绕过

`src/coevo/workspace/paths.py:88-91, 122-126, 149-153`

```python
if ".." in self.quarantine_root.split("/"):
    raise WorkspacePathError(...)
```

**问题**：只检查 `/` 分割。Windows 的 `quarantine_root="a\\..\\b"`（反斜杠）通过校验。`PurePosixPath` + `as_posix()` 之后还是 `\\`，不会归一化到 `/`。

**修法**：用 `pathlib.PurePath` / `os.path.normpath` 统一化路径分隔符再做 `".." in parts` 检查；或者在 Windows 上额外加 `\\` 检测。

### 4.5 [ROB-5] `_one_year_after` 失败时返回原 ISO 字符串而不 raise

`src/coevo/report/builder.py:290-298`

```python
def _one_year_after(iso_z: str) -> str:
    try:
        ...
        return future.isoformat().replace("+00:00", "Z")
    except Exception:
        return iso_z
```

**问题**：
1. 静默兜底 → 生成的 envelope `expires_at == created_at`，下一行 `if expires <= created: raise AgentPackageEnvelopeError(...)` 会触发（恰好捕获），但报错信息不直接指向 `_one_year_after`。
2. `from datetime import datetime, timedelta, timezone` 函数内 import，函数顶部已经 `import datetime as dt` —— **重复 import，浪费一行**。
3. `Exception` 太宽。

**修法**：解析失败直接 raise `ReportBuilderError(f"failed to compute expires_at from {iso_z!r}: {exc}")`。把 datetime import 提到模块顶层。

### 4.6 [ROB-6] `MergeEngine.merge_and_commit` 用 `removesuffix` 但未 catch AttributeError

`src/coevo/merge/__init__.py:818-820, 927-929`

```python
prior_history = receipt_repository.verified_history(
    trusted_time=dt.datetime.fromisoformat(
        decided_at.removesuffix("Z") + "+00:00"
    )
)
```

**问题**：
1. `str.removesuffix` 是 Python 3.9+；如果未来切到 3.8 环境会 `AttributeError`。
2. `decided_at` 可能非 `Z` 结尾或不是字符串 —— 当前 `_parse_utc` 已强制 `Z` 后缀，但 `merge_and_commit` 没有先调 `_parse_utc`。
3. 同一段代码在 `merge_and_commit` 内出现两次（line 818-820 和 927-929），重复定义 `trusted_time` 解析。

**修法**：抽 helper `_parse_decided_at(decided_at) -> dt.datetime` 复用；先校验 `decided_at` 以 `Z` 结尾再解析。

---

## 5. 优化建议（性能 / 可维护性）

### 5.1 [OPT-1] `merge/__init__.py` 1188 行单文件应拆分

US-10 用了多文件（`__init__` 1188 + `receipt` 672 + `repository` ~600），但 `risk` (506) / `supervision` (631) / `decision_brief` (1414) 全部塞在 `__init__.py`。建议拆为：

```
merge/__init__.py       ~150 (re-exports)
merge/models.py         MergeDecision, FieldMerge, MISSING, MergeRecord, MergeProposal, MergeCommitOutcome, _master_revision
merge/engine.py         MergeEngine (1188 → 800+)
merge/risk_bridge.py    _validate_bound_risk
merge/repository.py     (已存在)
merge/receipt.py        (已存在)
```

同理 `risk` 拆 `risk/{models,analyzer,helpers}.py`；`decision_brief` 拆 `decision_brief/{models,content,template,repository,service}.py`。

### 5.2 [OPT-2] 三个"from src.coevo.X"路径耦合反模式

`src/coevo/merge/__init__.py:101` 等处：

```python
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.import_transaction import ImportStep
from src.coevo.protocol.processed_package_store import ...
```

**问题**：所有跨包引用都写 **绝对路径** `src.coevo.X.Y`，而不是 `coevo.X.Y` 或相对 import。两种用法并存（identity / task_flow 内部用 `from .models`，但跨包用 `from src.coevo.X`），混用导致 import graph 难以静态分析。

**修法**：统一用 `from coevo.X import ...`（基于 `pyproject.toml` 的 `[tool.setuptools.packages]` 把 `src.coevo` 注册为 `coevo`），或在 `src/__init__.py` 显式 re-export。

### 5.3 [OPT-3] `decision_brief._validate_stored_brief` O(n) 重复走 hash 链

`src/coevo/decision_brief/__init__.py:1106-1147`

```python
def _validate_stored_brief(brief):
    ...
    WpsDocumentRequest(...)   # ← 重建 WpsDocumentRequest 实例仅为了触发 __post_init__
    ...
```

**问题**：
1. 对每个 `brief` 都重建 4 个 WPS request dataclass，纯为了触发 `__post_init__` 验证 —— 浪费 O(n) dataclass 构造。
2. `_validate_content_model` 又对每个 conclusion 重建 `BriefConclusion` —— 同样的反模式。
3. `_clone_brief` 调用 `_validate_stored_brief` 然后又**逐字段重新 dataclass 构造** —— 双重构造。
4. 整段 `repository.get` / `create` / `revise` 每次都跑完整 hash chain 验证 —— 单 brief 没问题，但若有 100 个 brief，重复构造就是 100×。

**修法**：抽 `_validate_wps_request(request)` 辅助函数（只调 `__post_init__`），不创建新实例；`_clone_*` 系列直接 `dataclasses.replace` + 一次性 `_validate_stored_brief` 验证。

### 5.4 [OPT-4] `IdentityRepository._insert_audit` 序列化两次

`src/coevo/identity/repository.py:97-110`

```python
event = {...}
event_hash = hashlib.sha256(json.dumps(event, sort_keys=True, ...).encode()).hexdigest()
self.connection.execute("INSERT INTO ... event_hash, ... VALUES (...,?,?,?,?,?,?,?,?,?,?)", (... event["event_hash"],))
```

**问题**：`event` dict 中先放 `event_hash`，然后序列化；但**序列化时不包含 `event_hash` 字段**（因为 `event_hash` 是 hash of `event` without `event_hash` itself），所以 `json.dumps(event, ...)` 在 hash 之前就把 `event_hash` 也 dump 了 —— **但 `event_hash` 此时还没设置**，所以这次 dump 不含 `event_hash` 字段 —— OK，逻辑正确。**但** `event["event_hash"]` 在 hash 之后才被设置，**insert 时的 dict 序列化结果与 hash 时的结果不一致**！审计链上的 `event_hash` 是用不含 `event_hash` 的 dict 算的，但写到 DB 的 row 里 `event_hash` 字段是对的。

验证：插入的 `event_hash` 列存的是正确的 hash（line 109）—— **OK**，但 `_internal_audit_valid` 重算时（line 137）用的也是不含 `event_hash` 的 sub-dict —— **OK**。整体一致，只是初看容易误会。

**修法**：加一行注释明确说明"event_hash 字段不参与自身 hash 计算"。

### 5.5 [OPT-5] `MergeEngine` `merge` 是 O(n²) per field

`src/coevo/merge/__init__.py:636-715`：每条报告字段 → 每条 baseline 字段 → 一次比对。当前用三个独立 helper 写死顺序，复杂度 O(report × baseline) per field × 字段数。`baseline.work_packages` + `dependencies` 都是 10² 量级时还好，到 10⁴ 时成 10⁸。

**修法**：先建 `{field_path: current_value}` 索引，再 per-field O(1) 查；只在 `field_merges` 阶段才需要对比。

### 5.6 [OPT-6] `_canonical_plain` + `_encode` 多次走同一个 dict

`src/coevo/merge/receipt.py:437-500` (`_freeze_value` / `_copy_domain_value`)

每个 domain object 走两次：先 `_copy_domain_value` 拷贝，再 `_freeze_value` 转换为 JSON-safe。两遍都递归走相同结构。`ProjectBaseline` + 100 个 task 时，5000+ 节点 × 2 = 10000 次递归调用。

**修法**：合并为单次 `_clone_and_freeze(value)`，在递归同时做 copy + freeze。

---

## 6. 安全相关发现（已审计但需注意）

### 6.1 [SEC-1] `IdentityRepository._cleanup_failed_create` 静默 `except Exception`

`src/coevo/identity/repository.py:73-78`

```python
def _cleanup_failed_create(self) -> None:
    try:
        if ...:
            self.anchor.abort_pending()
    except Exception:
        pass
    for path in self.anchor.artifacts():
        path.unlink(missing_ok=True)
    self.database.unlink(missing_ok=True)
```

**问题**：cleanup 失败时静默吞，外部调用者看到的是"create failed"但 audit anchor / db 文件可能残留 → 攻击者下次 `open()` 会被 `IdentityRepository.__init__` 报"refusing to create over existing state"。

**修法**：log 一次 warning 后再 `pass`（用 `logging.getLogger(__name__).warning`）。

### 6.2 [SEC-2] 私钥 helper 路径校验用 `candidate.resolve(strict=True)` 但 ROOT 是 `Path(__file__).resolve().parents[3]`

`src/coevo/identity/private_keys.py:48, 277-288`

```python
ROOT = Path(__file__).resolve().parents[3]
STORE_HELPER = ROOT / "scripts" / "store_private_key.ps1"
...
self.helper_path = candidate.resolve(strict=True)
controlled = STORE_HELPER.resolve(strict=True)
if self.helper_path != controlled:
    raise PrivateKeyHandleError("private-key helper path is not controlled by the repository")
```

**问题**：
1. `STORE_HELPER_SHA256 = "2dc55768..."` 是写死的 hardcoded 哈希 —— 若 PowerShell 脚本修改后 hash 变更，**所有测试 fail**。这一点已是合规要求（"helper must be locked"），但对开发体验差。
2. `Path(__file__).resolve().parents[3]` 假设 `src/coevo/identity/private_keys.py` 的 `parents[3]` 是 repo root，**依赖目录结构**，跨 OS 安全。
3. `_powershell_executable` 用 `TOOLCHAIN_LOCK`（JSON）做 hash 校验，但 `TOOLCHAIN_LOCK` 本身是 `docs/dependencies/toolchain-lock.json` 写死，**没有签名保护**。

**修法**：维持 locked 模式（这是 fail-closed 需求），但加 **smoke test 钩子**：`make_quality_gate` 之前先验证 `toolchain-lock.json` 与实际 `powershell.exe` hash 一致。

### 6.3 [SEC-3] P1 fail-closed: SM3 用 SHA-256 替身, sign / verify 永远 raise

`src/coevo/protocol/sm2_sign.py:120-143, 240-264, 267-313`

`compute_sm3_digest` 名字是 SM3 实际返回 SHA-256；`sign_manifest` / `verify_signature` 永远 raise `AgentPackageCryptoUnavailableError`。这是设计上的 P1 fail-closed（AGENTS.md §6 禁 silent fallback），但 audit log 里的"manifest_sm3"实际是 SHA-256，可能让安全审计员困惑。

**建议**：在 audit record 里加 `digest_algorithm_actual="sha256"` 字段（不是 `manifest_sm3` 字段本身），让未来切真 SM3 时审计链可追溯。

---

## 7. 测试相关

### 7.1 已实测（pytest 6 次运行）

| Suite | Result | 备注 |
|---|---|---|
| unit (310 + 1 skip + 148 sub) | ✅ pass | 32s |
| integration (133 + 28 sub) | ✅ pass | 74s |
| security (90 + 14 sub) | ⚠️ **1 fail**：`test_current_project_audit_is_fully_sealed`（见 §4.1） | 164s |
| e2e (3) | ✅ pass | 64s |
| 全部 quality gate (`make quality`) | ❌ timeout > 600s | quality_gate.py 串行跑全部，security 部分单测就 164s |

**`make quality` 跑不完**：timeout 600s。quality_gate.py 串行运行 unit + security + integration + e2e，security 单测 164s、integration 74s、e2e 64s、unit 32s，总计 ~340s，加 + overhead 应该 < 600s，但实测 600s 不够 —— 可能 `make` 嵌套或 stdout flush 拖慢。

**建议**：改 quality_gate.py 跑 unit + security 并行（pytest-xdist），可省 100s+。

### 7.2 测试覆盖盲点（人工检查，未跑新增 case）

- **negative case 缺**：`FieldMerge` 接受 list/dict 当前未测；`WorkPackage.responsible_role` 为空时是否 raise 未测。
- **concurrent 缺**：`DecisionBriefRepository.revise` 和 `merge_and_commit` 都用 `Lock()`，但**没有并发测试**。若 US-14 / US-15 引入多线程 caller，这是个坑。
- **round-trip 缺**：`BriefContent.to_audit_record` / `to_dict` 没有 `from_dict` 路径 —— 一旦加了 persistence 层，序列化兼容性会出问题。

---

## 8. 优先级与建议行动

| 优先级 | 项 | 估时 | 风险 |
|---|---|---|---|
| **P0** | §3.1 build_signed_payload 真 stub bug | 30 min | 低（无生产 caller） |
| **P0** | §3.2 US-9 base_revision 漏校验 | 20 min | 中（破坏 AC-3 验收） |
| **P1** | §3.3 import_service 漏 raise | 15 min | 低（占位代码） |
| **P1** | §3.4 merge._reject 静默 except | 15 min | 低 |
| **P1** | §4.1 audit_seal 测试不可重入 | 60 min | 中（CI 阻塞） |
| **P2** | §4.2/4.3/4.4 鲁棒性 | 各 30 min | 中 |
| **P3** | §5.1-5.6 重构优化 | 4-6 hr | 中 |
| **P3** | §6.1-6.3 安全加强 | 1-2 hr | 中 |

---

## 9. 审查范围之外（已知遗漏 / 后续工作）

- US-4 / US-7 / US-8 / US-14 / US-15 仍是 `ready` / 未开始（BACKLOG.yaml）。本审查只看已完成代码。
- `loop/tool-audit.jsonl` 等治理文件未审查内容（属 audit chain 治理范畴）。
- `scripts/` 下 PowerShell 脚本（`store_private_key.ps1` / `identity_freshness.ps1` / `audit_signature.ps1`）未审查；属运维脚本层，下次 `_powershell_executable` 集成测试时另起一份审查。
- 已合并/已推送的 PR 不再回溯审查；本审查只针对当前 working tree。

---

**审查者备注**：本审查基于"实测 + 人工"，不引用未跑过的 docstring 数字。下次 commit 触发建议在 loop/DECISIONS.md 增补一行审查记录，但因 `CODE_REVIEW.md` 不在 §0 文档治理范围（**这是新文档，需要业务负责人裁决**是否纳入 §3 强约束目录），故**先不 commit**。
