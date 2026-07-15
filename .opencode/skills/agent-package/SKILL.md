---
name: agent-package
description: `.agent` 任务包的封装、加密、签名、版本、重放检测、冲突处理与原子导入；按需加载，协议变更必须同步 schema 与兼容性测试。
compatibility: opencode
metadata:
  project: coevo
  scope: mvp
---

## 权威文件

- `docs/protocol/agent-package-protocol.md`
- `docs/constraints/mandatory-technical-constraints.md`

## 实现守则

- 不允许自动运行包内可执行内容。
- 必须使用固定的 JSON 规范化（字段顺序、UTF-8、空白处理）。
- 接收人绑定在 Manifest 中显式声明，签名覆盖接收人标识。
- 包 ID + 序列号必须可全局去重；接收端必须做重放检测。
- 加密 / 签名使用已批准的国产 SM 算法接口；未批准前不得替换。
- 导入失败必须原子回滚（已落盘文件、配置、审计一并回退）。

## 协议变更守则

任何 `.agent` 协议字段调整都必须：

1. 更新 Schema 与版本号。
2. 更新协议版本判断逻辑。
3. 增加兼容性测试（旧版 ↔ 新版）。
4. 增加异常输入测试（损坏、过期、越权、穿越、压缩炸弹）。
5. 更新 `docs/traceability/requirements-test-matrix.md`。
6. 在 `loop/DECISIONS.md` 留痕。
