"""US-7 local cockpit service facade.

Scope
-----
Pure half of US-7: the *governance* layer that decides which cockpit
request is allowed and what the response body should be. The slice
stops at the dispatch boundary. HTTP server bring-up (``server.py``),
static rendering (``static.py``), state persistence
(``state_store.py``) and the WPS launcher (``wps.py``) implement
US-7-AC-2/AC-3/AC-4 + WPS-AC-4 + COCKPIT-OPS-1 and are wired by the
composition layer.

* No new dependency (Python stdlib only).
* All dataclasses are frozen + exact-type + ISO-8601 UTC `Z` time strings.
* Pure function: same (request, server_state, now) yields identical
  CockpitResponse.
* to_audit_record mirrors US-11/12/13/8/15/4 by EXCLUDING free-form
  body_html and artifact_path from the audit row.

AC mapping
----------
* AC-1 环回绑定 -- :meth:`CockpitFacade.start_server` rejects any
  ``bind_host`` other than ``"127.0.0.1"``.
* AC-2 静态资源本地化 -- :class:`CockpitServerConfig.static_root` is
  forced to be inside ``src/coevo/cockpit/static/``; any path
  traversal attempt is rejected.
* AC-3 完全断网 -- pure local Python stdlib; no third-party import.
* AC-4 无外部网络请求 -- path-traversal rejection + static-root
  whitelist.
* AC-5 项目列表 -- :attr:`CockpitRoute.LIST_PROJECTS`.
* AC-6 角色视图 -- :attr:`CockpitRoute.LIST_ROLES` /
  :attr:`CockpitRoute.ROLE_VIEW`.
* AC-7 任务/里程碑/交付物 -- :attr:`CockpitRoute.TASK_VIEW` /
  :attr:`CockpitRoute.MILESTONE_VIEW` + the ``RoleView`` snapshot.
* AC-8 WPS 允许列表 -- :class:`WPSAllowList` + :attr:`CockpitRoute.WPS_OPEN`.
* AC-9 客户端重启状态保持 -- :class:`CockpitServerState` snapshot
  is immutable; ``dispatch`` reads from the snapshot, not from disk.

Non-goals
---------
* The facade performs no IO: HTTP serving lives in ``server.py``,
  static rendering in ``static.py``, state persistence in
  ``state_store.py`` and WPS launch in ``wps.py`` (implemented
  slices US-7-AC-2/AC-3/AC-4, WPS-AC-4, COCKPIT-OPS-1)."""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from pathlib import Path

from .models import (ArtifactSummary, CockpitError, CockpitNotFoundError, CockpitRequest, CockpitResponse, CockpitResponseStatus, CockpitRoute, CockpitServerConfig, CockpitServerState, CockpitValidationError, LOOPBACK_HOST, MilestoneSummary, RoleView, STATIC_ROOT, TaskSummary, WPSAllowList, WorkspaceView, _HEX_64, _SAFE_ID, _hash_path)

from .facade import (CockpitFacade)

from .server import CSRF_HEADER_VALUE, CockpitHttpConfig, CockpitHttpServer, CockpitSessionManager, SingleInstanceLock, now_utc_iso_z, resolve_static_path
from .state_store import CockpitStateStore, deserialize_views, serialize_views
from .wps import MAX_DOCUMENT_BYTES, WpsLaunchDecision, WpsLaunchResult, WpsLauncher
