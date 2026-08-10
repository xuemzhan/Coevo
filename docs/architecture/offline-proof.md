# 断网黑盒证明（Offline Black-Box Proof）

> 状态：生效（2026-08-10，REVIEW2-9）
> 适用范围：`tests/e2e/test_review2_9_offline_blackbox.py` 与本地驾驶舱的离线边界。

## 1. 证明程序

启动真实 `CockpitHttpServer`（127.0.0.1），在**捕获每个 socket connect 目标**的
前提下走查核心表面：index、/static/style.css、/static/app.js、读 API、
被拒绝的写路径（wps_open 无 confirm）。断言：

- `external_requests = 0`（所有 connect 目标均为 127.0.0.1/::1）；
- `loopback_requests = N`（本地服务确实被访问，防止"零请求假装通过"）；
- `missing_local_assets = 0`（引用的静态资源均 200）；
- `runtime_downloads = 0`（从未打开非环回 socket）；
- 服务字节内无外部 URL 引用（http(s)://、CDN、字体、统计、更新检查）。

## 2. 局限与生产验收

进程内 socket 捕获是 CI 可复现证明；生产验收应在受控主机上以防火墙白名单
（仅允许 127.0.0.1）复跑同一走查并核对同一指标。这属于部署验收步骤，不影响本
契约的有效性。

## 3. 与既有离线测试的关系

- `tests/e2e/test_offline_baseline.py`：stdlib-only 与工程底座；
- `tests/e2e/test_cockpit_offline_frontend.py`：静态资源本地化与无外部 URL（内容层）；
- 本测试：**socket 连接层**黑盒证明（行为层），三者互补。

## 4. 变更纪律

任何引入运行时网络访问、CDN/字体/统计/更新检查的改动，必须同步本契约并让本测试
变红（fail-closed）。
