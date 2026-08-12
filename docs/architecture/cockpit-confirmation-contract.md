# 驾驶舱确认契约（Cockpit Confirmation Contract）

> 状态：生效（2026-08-12，PRODUCT-REVIEW T-10）。
> 范围：`PENDING_CONFIRM` 路由（`/api/pending_confirm`）的处理器契约、授权
> 与审计语义，以及 demo/生产注入隔离。

## 1. 路由语义（fail-closed）

| 条件 | 结果 |
|---|---|
| 未配置处理器 | `NOT_AVAILABLE`（503），绝不假装执行 |
| `action=confirm` 且处理器返回 `approved` | `STARTED`（200） |
| `action=reject` 且处理器返回 `rejected` | `DENIED`（403） |
| 处理器异常 / 返回未知结果 | `ERROR`（500） |
| `action` 非法 | `BAD_REQUEST`（400） |

所有请求必须携带有效会话令牌 + `Origin`（环回）+ `X-Requested-With`，并写入
审计记录（`to_audit_record`，仅存哈希/计数）。

## 2. 处理器契约

`PendingActionHandler`（`src/coevo/cockpit/facade.py`）：

```python
class PendingActionHandler(Protocol):
    def __call__(self, action: str, *, subject: str) -> dict[str, str]: ...
```

- `action`：`"confirm"` 或 `"reject"`；
- `subject`：发起会话的身份声明（签发时绑定，令牌不可反推；由服务器在
  分发时从会话读取并透传）；
- 返回：必须含 `decision` 键，取 `"approved"` / `"rejected"`；
- 处理器由**可信组合根**注入，禁止从请求数据构造。

## 3. 授权与身份（PRODUCT-REVIEW T-08/T-09）

- 会话携带 `subject`（身份声明，签发时绑定，令牌不可反推）；
- 生产处理器必须配合 `PolicyAuthorizer`（`src/coevo/identity/service.py`，
  fail-closed：未知 actor/权限一律拒绝），以透传的 `subject` 判定确认权限；
- demo 模式（`--serve-gate`）注入演示处理器并绑定 `DEMO_ACTOR`；
  生产入口（`src/coevo/app/production.py`）不内置处理器。

## 4. 注入隔离守卫

- `tests/unit/test_cockpit.py::PendingActionContractTests`：
  处理器协议存在、demo 是唯一注入点、生产入口不含处理器、facade 缺省
  fail-closed；
- `tests/unit/test_cockpit.py::PendingConfirmTests`：无处理器/批准/驳回/
  非法动作/异常五条路径全覆盖 + subject 透传；
- `tests/integration/test_cockpit_http_server.py`：HTTP 分发时从会话读取
  subject 并透传给处理器的集成验证。
