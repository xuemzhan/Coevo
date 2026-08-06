# `workspace/` — 工作区（US-6）

## 定位

导入结果到工作区路径与注册表的纯函数转换：项目/角色隔离、安全 ID、防穿越、
重复导入幂等（AC-4/5/7/8）。

## 职责边界

- **in scope**：路径策略（Quarantine/Workspace 路径）、注册表、初始化服务；
- **out of scope**：实际文件落盘（由持久化层承担，本模块纯字符串路径）。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `models.py` | `WorkspaceEntry`、`WorkspaceRegistry`、`WorkspaceRole`、`InitOutcome` | 角色绑定/条目/注册表（索引化查询，by_package O(1) 分组）/初始化结果 |
| `paths.py` | `sanitize_id()`、`QuarantinePath`、`WorkspacePath`、`build_paths()` | 安全路径策略：安全 ID 验证、POSIX+Windows 双方言防 `..` 穿越、默认根 |
| `init_service.py` | `WorkspaceInitService.init_from_import()` | 初始化服务：非 COMMITTED 拒、同包幂等、路径构造统一助手（失败关闭传播） |

## 关键入口与数据流

```
ImportOutcome（COMMITTED）→ WorkspaceInitService.init_from_import
  → 路径校验（安全 ID + 防穿越）→ WorkspaceRegistry（重复 (project, role) 拒绝）
  → InitOutcome → 持久化层落盘
```

- `WorkspaceInitService.init_from_import()`；
- `WorkspaceRegistry.register/get/by_package`；
- `build_paths()` — 构造隔离区/工作区/临时区等九类标准目录路径。

## 安全与不变量

- 非 COMMITTED 事务不得释放工作区（AC-4）；
- 同一任务包重复导入不得重复创建任务（AC-8 幂等）；
- 路径拒绝绝对路径、`..`、设备前缀、符号链接越界（POSIX + Windows 双方言）；
- 工作区目录用系统生成唯一 ID，不只用用户输入名称（强制约束 §6.1）。

## 测试覆盖

- `tests/unit/test_workspace_init.py`（30 项：QuarantinePath/WorkspacePath/
  注册表/init facade/build_paths）；
- `tests/integration/test_agent_package_atomic_import.py`（导入→初始化联动）。

## 依赖与下游

- **上游依赖**：`protocol`（ImportOutcome/事务）；
- **下游消费者**：`progress_capture`（工作区扫描）、`cockpit`（工作区视图）、
  `examples/` 演示。
