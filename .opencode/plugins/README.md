# Loop Guard — 第二道防线

| Hook | 拦截面 | 触发 |
|---|---|---|
| `tool.execute.before` | bash 命令 + read/edit/write 文件路径 | 命中危险命令或受保护路径即抛错 |

## 拦截清单（同步建议文档第二节）

危险命令：

- `git push / git reset --hard / git clean`
- `rm -rf / del /s / format <drive>`
- `curl / wget / Invoke-WebRequest`
- `npm/bun/pip/pip3/uv pip/go get install`

受保护路径：

- `*/secure/*`、`*/keys/*`
- `*.env`
- `ProgramData\opencode\`、`ProgramData/opencode/`
- `.git/hooks/`（避免自动 hook 注入）

## 升级路径

- 当某条命令需要列入允许名单时，**不要在本插件里直接白名单**；应回到项目级 `opencode.jsonc` 的 `permission.bash` 用 `allow:` 精确放行，并在此处增补注释。
- 新增保护路径请同步更新 `docs/constraints/mandatory-technical-constraints.md`。

> 这不是 OS 沙箱。沙箱仍由开发账户权限、隔离虚拟机、代码仓库保护与制品审查构成。
