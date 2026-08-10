# 交付门禁契约（Delivery Gate）

> 状态：生效（2026-08-10，REVIEW2-11）
> 适用范围：`scripts/release_check.py` 的 `delivery_artifacts` 检查与发布边界。

## 1. 硬失败（critical）

`release_check.py` 的 `delivery_artifacts` 检查在以下任一条件时拒绝发布：

- 跟踪树中存在运行时/密钥类制品：`__pycache__/`、`*.pyc`、`*.db(-wal|-shm)`、
  `*.pdb`、`helper.exe`、`loop/private-key-handles-*.json`；
- 生产组合根 `scripts/run_cockpit.py` 引用 GmSSL 原型提供者
  （原型密码只允许出现在 demo/测试路径，REVIEW2-6）；
- secret-scan 的夹具豁免超出 `tests/` + `loop/` 最小前缀。

## 2. 警告（warning）

- Win7 分离文档 `docs/architecture/win7-compat-branch.md` 缺失发布标记
  （独立 / 发布），提示补充分离产物与锁定说明。

## 3. 使用

发布前运行 `python scripts/release_check.py`（含 git clean、版本、状态、backlog、
audit fully-sealed、secret scan、traceability、delivery_artifacts）。

## 4. 守卫测试

`tests/unit/test_release_check.py` 新增：真实仓库无禁用制品、伪造跟踪制品被拒、
生产 runner 引用原型被拒。

## 5. 变更纪律

任何新增交付/打包流程必须同步本契约与 `delivery_artifacts` 检查；不得以"本地运行
状态"为由把运行时缓存、密钥句柄或原型密码带入发布包。
