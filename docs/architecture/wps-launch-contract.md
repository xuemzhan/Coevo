# WPS 启动链路契约（WPS Launch Contract）

> 状态：生效（2026-08-10，REVIEW2-4）
> 适用范围：`src/coevo/cockpit`（facade / server / wps launcher）的 WPS 打开边界。

## 1. 结果语义（不再使用"accepted"冒充"已启动"）

CockpitFacade 的 `WPS_OPEN` 路由在注入 `WpsLauncher` 后返回真实结果语义：

| 语义 | 触发条件 | HTTP |
|---|---|---|
| `STARTED` | launcher 校验通过且文档已启动（`decision=ok`） | 200 |
| `DENIED` | 扩展名/路径/工作区边界拒绝 | 403 |
| `NOT_AVAILABLE` | 未配置 launcher，或可执行文件不可用 | 503 |
| `ERROR`/`failed` | 启动异常/超时/launcher 抛错 | 500 |

未注入 launcher 时 `WPS_OPEN` 一律返回 `NOT_AVAILABLE`，**绝不返回假的 "accepted"**。

## 2. 边界职责

- `WpsPolicy`（WPSAllowList + 工作区相对路径 + 常规文件 + 大小上限）由
  `WpsLauncher.launch` 执行（含 symlink/reparse 拒绝）；
- `WpsLauncher` 负责真实子进程启动、超时（30s）、返回码与审计字段；
- `CockpitFacade._wps_open` 只做路由/鉴权语义与结果映射，不拼接 shell 命令；
- HTTP 层（server）把 `wps_launcher` 注入 facade，敏感操作仍需 `confirm=true`
  + 会话 + CSRF/Origin 校验（REVIEW2-5 继续补黑盒矩阵）。

## 3. 守卫测试

`tests/unit/test_cockpit.py::WPSOpenTests`（REVIEW2-4 扩展）强制：

- 无 launcher → `NOT_AVAILABLE`；
- launcher `ok` → `STARTED`（含 returncode）；
- launcher `denied` / `not_available` / `error` 映射正确；
- launcher 抛异常 → fail-closed `ERROR`。

真实进程启动语义由 `WpsLauncher` + `tests/unit/test_wps_launcher.py` 覆盖。

## 4. 变更纪律

任何改变 WPS 结果语义、鉴权顺序或启动边界的改动，必须同步本契约并在
`loop/DECISIONS.md` 留痕。
