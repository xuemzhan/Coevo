# `cockpit/` — 本地驾驶舱（US-7）

## 定位

环回绑定的本地 HTTP 驾驶舱：视图快照、bearer-token 会话、状态持久化、静态资源
与受控 WPS 文档启动。完全断网可运行，前端资源全部本地化。

## 职责边界

- **in scope**：HTTP 服务生命周期、会话/CSRF/Host/Origin 治理、状态快照落盘与
  重启恢复、静态资源策略与缓存、WPS 启动允许列表；
- **out of scope**：领域数据持久化（各领域 store）、在线/云端同步。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `CockpitRoute/Request/Response`、`WorkspaceView`、`WPSAllowList` | 路由/响应状态/视图快照/配置（环回强制、WPS 允许列表） |
| `facade.py` | `CockpitFacade.dispatch/to_audit_record` | 纯函数路由分发与审计投影 |
| `server.py` | `CockpitHttpServer`、`CockpitRequestHandler`、`SingleInstanceLock` | 单实例锁（心跳刷新 + 存活校验）、HTTP 处理器、服务生命周期、访问审计日志 |
| `sessions.py` | `CockpitSessionManager` | bearer-token 会话（过期/轮换/上限） |
| `state_store.py` | `CockpitStateStore` | 状态 JSON 原子持久化（周期快照 + 停机落盘） |
| `static.py` | `resolve_static_path()`、`_StaticAssetCache` | 静态资源路径策略与有界 FIFO 缓存 |
| `wps.py` | `WpsLauncher` | 受控 WPS 启动（允许列表扩展名、超时、失败关闭、dry-run） |

## 关键入口与数据流

```
浏览器(index?token=) → GET/POST → Host/Origin/CSRF 校验 → 会话校验
  → CockpitFacade.dispatch → 视图/动作 → 状态快照(周期+停机) → 审计访问日志
```

- `CockpitHttpServer.start()/stop()` — 优雅启停（SIGINT/SIGTERM/CTRL_BREAK）；
- `CockpitFacade.dispatch()` — 项目/角色/任务/里程碑视图 + WPS 打开；
- `SingleInstanceLock` — O_EXCL 创建 + 60s 心跳 + 陈旧锁双判定接管；
- `scripts/run_cockpit.py --print-token` — 签发一次会话令牌（服务端只存摘要）。

## 安全与不变量

- **只绑定 `127.0.0.1`**，非环回配置失败关闭（强制约束 §5.1）；
- 所有响应带 `X-Content-Type-Options: nosniff`；会话/API 响应
  `Cache-Control: no-store` + `Referrer-Policy: no-referrer`（静态资源可覆盖为
  `public, max-age=300`）；首页保留 CSP（`default-src 'self'`…）；
- API 需 token + Host/Origin 白名单 + CSRF 头（`X-Requested-With: coevo-cockpit`）；
- 并发有界（默认 16，饱和 503）；单实例锁防双写；状态快照崩溃不丢多于一周期；
- 访问日志不落 token/URL 查询；WPS 只允许列表内扩展名 + 工作区内相对路径。

## 测试覆盖

- `tests/unit/test_cockpit.py`、`test_cockpit_http.py`、`test_cockpit_state_store.py`；
- `tests/integration/test_cockpit_http_server.py`、`test_cockpit_state_persistence.py`；
- `tests/e2e/test_cockpit_launcher.py`、`test_cockpit_offline_frontend.py`。

## 依赖与下游

- **上游依赖**：`workspace`（视图数据）、`protocol`（导入）、`config.py`；
- **下游消费者**：`scripts/run_cockpit.py`、`scripts/cockpit-watchdog.ps1`、
  `scripts/health_check.py`（/healthz 身份校验）、`examples/service-api`。
