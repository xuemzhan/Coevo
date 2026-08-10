# 驾驶舱 HTTP 认证黑盒矩阵（Cockpit HTTP Auth Matrix）

> 状态：生效（2026-08-10，REVIEW2-5）
> 适用范围：`src/coevo/cockpit/server.py` 的真实 HTTP 服务认证边界。

## 1. 矩阵（黑盒实测，非仅 facade 单测）

| 请求类型 | 必须具备 | 黑盒用例 | 期望 |
|---|---|---|---|
| 读（GET） | 会话 token | 无 token 读 /api/* | 401 |
| 写（POST wps_open） | 会话 + CSRF + Origin + 显式确认 | 无 token 写 | 401/403 |
| 写 | Host 校验 | 伪造 Host 的写请求 | 403 |
| 写 | CSRF + Origin 双头 | 缺任一（X-Requested-With 或 Origin） | 403 |
| 写 | 二次确认 | confirm != true | 403 |
| 写 | 会话有效 | 会话过期后重放 | 401 |
| 写 | token 未撤销 | 撤销后重放同一写请求 | 401 |
| 静态资源 | Host/路径/CSP | Host 伪造 / 路径穿越 | 403 |

## 2. 实现与守卫

矩阵由 `tests/integration/test_review2_5_http_auth_matrix.py` 对**真实 HTTP 服务**
黑盒执行（含成功基线用例，防止"全部拒绝"掩盖接线失效）。既有
`test_cockpit_http_server.py` 继续覆盖读路径、日志、锁、溢出等。

## 3. 变更纪律

任何改变会话/CSRF/Origin/Host/确认语义的改动，必须同步本矩阵并新增对应黑盒用例；
不得以"仅环回绑定"为由弱化鉴权。
