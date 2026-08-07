# US-16-AC-9 切片计划：K8s CRD 纸面清单生成器（CTAF §14.2 / §16.4 / M9）

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。本轮只跑
> 增量门禁（fmt + lint + 定向测试），豁免留痕。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-9-k8s-crd-listing-v0.1`
- 用户故事：US-16【框架层】——把框架声明（能力 / Tool / Policy / Plan）导出为
  确定性、可哈希的纸面清单（规范 JSON + YAML 渲染子集），供文档与合规使用；
  **仅纸面清单，不承诺 reconcile loop**（§16.4 M9 承诺范围）。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-9.1 | 声明式清单生成（JSON + YAML 子集），与 K8s 解耦 | test_listing_generation_and_yaml |
| AC-9.2 | 纯函数、确定性、listing_fingerprint 可哈希 | test_listing_deterministic_hash |
| AC-9.3 | opt-in 沙箱：零 IO 副作用、只读输入 | test_listing_no_side_effects |
| AC-9.4 | 清单结构校验（白名单/重复键/未知字段/BOM/超限） | test_listing_validation |
| AC-9.5 | 纯函数 / 离线 / stdlib / L17 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/k8s_listing.py`：ListingInput（能力/Tool/Policy/Plan
声明集合 + generated_at）、generate_listing_json / generate_listing（规范 JSON
字节）/ listing_fingerprint / render_yaml（安全 YAML 子集发射器）/
validate_listing_bytes（严格解析）。新增 `docs/framework/k8s-crd-listing.md`；
更新模块文档（L17）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/k8s_listing.py`；修改 `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_k8s_listing.py`
- 新增 `docs/framework/k8s-crd-listing.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- 生成：空集合与混合集合均产出稳定清单；YAML 渲染确定性、字符串安全引号；
- 哈希：同一输入指纹一致；输入变化指纹变化；生成字节与指纹一致；
- 校验：重复键、未知顶层/spec 字段、BOM、超限（>64KiB）拒绝；合法清单通过；
- 副作用：生成函数不写文件/不联网（纯函数，测试断言无 IO 导入）；
- L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- 清单是声明导出物，不执行任何 K8s 逻辑（纸面清单边界）；YAML 发射器必须
  安全引号（防注入式字符串破坏结构）；
- 确定性哈希用于审计/版本比对；生成器零 IO；
- 零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- reconcile loop / K8s 控制器（明确不承诺）；M8 跨组织演练（外部协调型交付，
  留待 staging 环境）；A2A gossip / MCP-B（v0.5）；`.agent` wire 改动。

## 8. 可验证完成条件

- `python -m unittest tests.unit/test_framework_k8s_listing` 全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 US-16 | AC-9 行；security-reviewer 无 Critical/High。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-9 k8s crd paper listing generator (M9)`。

## 10. 审查门

- security-reviewer：**是**（YAML 引号安全 / 清单结构校验边界）；
- protocol-reviewer：**否**（不触碰 wire）。
