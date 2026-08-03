# US-7-AC-1 Slice Plan: local cockpit service facade

> Loop-engineer PLAN 阶段产物, 2026-08-01.
> 对应 BACKLOG items[US-7-AC-1].test_cockpit.
> 本切片遵守 AGENTS.md §1 文档优先级与 §2 七阶段; 不修改 .agent wire, 不修改
> 密码方案, 不修改既有模块.

## 1. 用户故事与 AC

US-7: "本地驾驶舱 - 完全离线的多项目、多角色工作界面"
1. 本地服务仅绑定环回地址;
2. 所有前端脚本、样式、图标和字体均本地化;
3. 完全断网状态下界面正常运行;
4. 不产生任何外部网络请求;
5. 左侧导航列出本地全部项目和角色;
6. 点击项目或角色可切换独立工作视图;
7. 用户可查看任务、里程碑、交付物和当前状态;
8. 用户可通过允许列表调用 WPS 打开工作文档;
9. 客户端重启后项目状态保持.

## 2. 切片范围

### 2.1 新增模块

- `src/coevo/cockpit/__init__.py` (≤ 1000 行, 与 US-11/12/13/8/15/4 单文件风格一致)
- `src/coevo/cockpit/static/` 静态资源目录 (HTML/CSS/JS/icons, 内联 base64 或纯文本, 无外部 URL)
- `tests/unit/test_cockpit.py` (≥ 12 测试)

### 2.2 不修改

- 既有 `src/coevo/{identity,protocol,workspace,report,merge,risk,supervision,decision_brief,progress_capture,audit_governance,orchestrator,task_flow,task_decomposition,talent}` 等任何模块
- `.agent` wire / `loop/audit-signing.json` / `loop/audit-head.{json,p7s}`
- `toolchain-lock.json` (无新增依赖; 用 Python 标准库 `http.server` + `socketserver`)

### 2.3 边界

- 不引入 web 框架 (Flask/FastAPI 等); 用 `http.server.BaseHTTPRequestHandler` 实现
- bind 到 `127.0.0.1` 强制环回 (AC-1 fail-closed: 0.0.0.0 拒绝)
- 静态资源白名单只允许 `src/coevo/cockpit/static/` 目录内的文件 (AC-2 隔离, 防止 path traversal 跳出 cockpit)
- WPS 允许列表只允许 `*.docx` / `*.doc` / `*.xlsx` / `*.xls` / `*.pptx` / `*.ppt` (AC-8); 不允许 `.exe` / `.bat` / `.ps1` / `.js`
- 安全等级 security_review=true; 涉及环回绑定 + 路径隔离 + WPS allow-list

## 3. 数据模型

```text
CockpitRoute (Enum, closed set; AC-5/6/7/8)
  LIST_PROJECTS       -- 列出本地全部项目 (AC-5)
  LIST_ROLES          -- 列出项目的角色 (AC-6)
  PROJECT_VIEW        -- 项目视图 (AC-7)
  ROLE_VIEW           -- 角色视图 (AC-6/7)
  TASK_VIEW           -- 任务视图 (AC-7)
  MILESTONE_VIEW      -- 里程碑视图 (AC-7)
  WPS_OPEN            -- 调用 WPS (AC-8)

CockpitRequest (不可变)
  route                -- CockpitRoute
  project_id           -- str (空 if LIST_PROJECTS)
  role_id              -- str (空 if LIST_PROJECTS / LIST_ROLES)
  task_id              -- str (空 if not TASK_VIEW)
  artifact_path        -- str (空 if not WPS_OPEN)
  ts                   -- ISO-8601 UTC 'Z'

CockpitResponseStatus (Enum)
  OK                   -- 200 + 渲染 HTML
  NOT_FOUND            -- 404 (project_id / role_id 不存在)
  BAD_REQUEST          -- 400 (字段非法)
  DENIED               -- 403 (path traversal / 非 allow-list)
  NOT_BOUND            -- 403 (server 未绑 127.0.0.1)
  ERROR                -- 500

CockpitResponse (不可变)
  status               -- CockpitResponseStatus
  body_html            -- str (渲染的 HTML; OK 状态才有)
  content_type         -- str (text/html; charset=utf-8)
  task                 -- str (状态描述; audit 可投影)
  payload              -- dict (结构化数据; audit 可投影)
  ts                   -- ISO-8601 UTC 'Z'

WorkspaceView (AC-7)
  project_id           -- safe-id
  display_name         -- str
  roles                -- tuple[str, ...]
  task_count           -- int
  milestone_count      -- int
  artifact_count       -- int

RoleView (AC-6/7)
  role_id              -- safe-id
  project_id           -- safe-id
  display_name         -- str
  current_tasks        -- tuple[TaskSummary, ...]
  milestones           -- tuple[MilestoneSummary, ...]
  artifacts            -- tuple[ArtifactSummary, ...]

TaskSummary
  task_id              -- safe-id
  title                -- str
  status               -- str
  due_at               -- str
  assignee_role_id     -- safe-id

MilestoneSummary
  milestone_id         -- safe-id
  title                -- str
  due_at               -- str
  completed            -- bool

ArtifactSummary
  path                 -- str
  role                 -- str ("document" | "feedback" | "artifact" | "dependency")
  media_type           -- str
  size_bytes           -- int
  digest_hex           -- 64-hex

CockpitServerConfig
  bind_host            -- str (必须 127.0.0.1; 否则 raise)
  bind_port            -- int (1..65535; 默认 12701)
  static_root          -- Path (必须 src/coevo/cockpit/static/; 否则 raise)
  max_request_bytes    -- int (默认 65536; DoS guard)
  request_timeout_sec  -- int (默认 5)

CockpitServerState (不可变快照)
  config               -- CockpitServerConfig
  workspace_views      -- tuple[WorkspaceView, ...]
  started_at           -- ISO-8601 UTC 'Z'
```

## 4. 服务层

```text
class CockpitFacade:
    @staticmethod
    def dispatch(request: CockpitRequest, *,
                 server_state: CockpitServerState,
                 now: str) -> CockpitResponse:
        """AC-5/6/7/8: dispatch a cockpit request to a response.

        Fail-closed on:
        - server_state.config.bind_host != '127.0.0.1' (AC-1)
        - request.project_id / role_id 不在 server_state.workspace_views
        - request.route == WPS_OPEN && artifact_path 不在 WPS allow-list
        - request.artifact_path 含 '..' 或 absolute path
        """

    @staticmethod
    def start_server(*,
                     bind_host: str = '127.0.0.1',
                     bind_port: int = 12701,
                     workspace_views: tuple[WorkspaceView, ...] = (),
                     now: str) -> CockpitServerState:
        """AC-1/AC-9: bind to loopback only; raises if bind_host != '127.0.0.1'.
        Snapshots workspace_views (immutable) for later dispatch calls.
        """

class WPSAllowList:
    ALLOWED_EXTENSIONS   -- frozenset[str] = {'.docx', '.doc', '.xlsx', '.xls',
                                           '.pptx', '.ppt', '.rtf', '.pdf'}
    ALLOWED_MIME_PREFIX  -- frozenset[str] = {'application/vnd.openxmlformats-officedocument',
                                            'application/msword',
                                            'application/vnd.ms-excel',
                                            'application/vnd.ms-powerpoint',
                                            'application/pdf',
                                            'text/'}

    @staticmethod
    def is_allowed(path: str) -> bool:
        """AC-8: check extension + (if mime available) mime prefix.
        Reject .exe / .bat / .ps1 / .js / .vbs / .scr / .jar / etc.
        """

CockpitFacade.to_audit_record(request, response) -> dict:
    """审计投影: 保留 status / route / project_id / role_id; 排除 body_html
    + artifact_path (避免泄露文件路径)."""
```

## 5. AC 映射

| AC | 实现位置 | 失败模式 |
|---|---|---|
| AC-1 环回绑定 | start_server 强制 bind_host='127.0.0.1' | 其它地址 -> ValidationError |
| AC-2 静态资源本地化 | start_server.static_root 强制 src/coevo/cockpit/static/ | 其它路径 -> ValidationError |
| AC-3 完全断网 (离线) | 纯本地 Python 标准库 + 无第三方 import | -- |
| AC-4 无外部网络请求 | 静态资源白名单 + path traversal 拒绝 | '..' 或 absolute path -> DENIED |
| AC-5 项目列表导航 | LIST_PROJECTS + workspace_views 列表 | -- |
| AC-6 项目/角色视图切换 | LIST_ROLES + ROLE_VIEW | role_id 不在 -> NOT_FOUND |
| AC-7 任务/里程碑/交付物展示 | TASK_VIEW / MILESTONE_VIEW / RoleView.current_tasks | task_id 不在 -> NOT_FOUND |
| AC-8 WPS 允许列表调用 | WPS_OPEN + WPSAllowList.is_allowed | 扩展名不在 -> DENIED |
| AC-9 客户端重启状态保持 | workspace_views snapshot + dispatch 用快照 (不读 disk) | -- |

## 6. 测试点 (≥ 12)

1. test_cockpit_route_closed_set (AC-5/6/7/8)
2. test_start_server_rejects_non_loopback_bind (AC-1)
3. test_start_server_rejects_external_static_root (AC-2)
4. test_start_server_snapshots_workspace_views (AC-9)
5. test_dispatch_list_projects_returns_workspace_views (AC-5)
6. test_dispatch_list_roles_unknown_project_returns_not_found (AC-6)
7. test_dispatch_role_view_returns_role_summary (AC-6)
8. test_dispatch_task_view_unknown_returns_not_found (AC-7)
9. test_dispatch_wps_open_allowed_extension_succeeds (AC-8)
10. test_dispatch_wps_open_denied_extension_rejected (AC-8)
11. test_dispatch_wps_open_path_traversal_rejected (AC-4)
12. test_to_audit_record_excludes_sensitive_body (AC-7 审计投影)
13. test_pure_function_determinism_same_request_same_response (质量)
14. test_static_root_must_be_inside_cockpit_static (AC-2)

## 7. 风险与缓解

- R1 (AC-2 静态资源本地化测试): 本切片不写实际的 HTML/CSS/JS 文件 (避免引入 SVG/字体二进制), 只测 static_root 强制路径; UI 实际渲染留给后续 AC.
- R2 (AC-8 WPS 允许列表扩展名白名单): 不依赖实际 WPS 安装; 仅测试 is_allowed(path) 函数行为.
- R3 (AC-9 状态保持): workspace_views 是 in-memory 不可变 tuple, 进程重启后由调用方注入; 本切片不实现 disk persistence (留给 US-7-AC-2).

## 8. 完成定义 (本切片)

- 所有 ≥ 14 项 unit 测试通过
- `python scripts/quality_gate.py --target quality` exit=0, audit chain fully-sealed
- 不修改既有模块 / 既有 wire / 既有密码 / 既有审计配置
- BACKLOG US-7-AC-1 status: ready → done
- STATE bump iteration + status done
- DECISIONS append 一段 finalize 段 (append-only)
- 追踪矩阵 US-7 行追加

## 9. 后续 AC 候选 (本切片不做)

- US-7-AC-2: 实际 HTML/CSS/JS 渲染 + 静态资源服务.
- US-7-AC-3: workspace_views 持久化 (state.json + 启动加载).
- US-7-AC-4: WPS 实际调用 (跨进程 subprocess + 受控白名单).
