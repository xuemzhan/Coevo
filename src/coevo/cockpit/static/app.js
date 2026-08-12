(function () {
  "use strict";

  var token = new URLSearchParams(location.search).get("token")
    || sessionStorage.getItem("cockpit_token")
    || "";
  if (token) {
    sessionStorage.setItem("cockpit_token", token);
    if (location.search) {
      history.replaceState(null, "", location.pathname);
    }
  }

  var REFRESH_INTERVAL_MS = 15000;
  var historyStack = [];
  var state = {
    projects: [],
    roleNames: {},
    roleCounts: {},
    milestoneProgress: {},
    taskFilter: "",
    currentTasks: [],
    activeProjectId: "",
    activeRoleId: "",
    refreshTimer: null,
    inTaskDetail: false,
    inFlight: false,
    lastSnapshotTs: "",
  };

  function readHashState() {
    var params = new URLSearchParams(
      (location.hash || "").replace(/^#/, "")
    );
    return {
      projectId: params.get("project") || "",
      roleId: params.get("role") || "",
    };
  }

  function pushHash(projectId, roleId) {
    var current = location.hash;
    var next = "#project=" + encodeURIComponent(projectId);
    if (roleId) {
      next += "&role=" + encodeURIComponent(roleId);
    }
    if (current !== next) {
      historyStack.push(current);
      if (historyStack.length > 50) {
        historyStack.shift();
      }
      location.hash = next;
    }
  }

  function api(path, options) {
    var headers = { "X-Cockpit-Token": token };
    var init = { headers: headers };
    if (options && options.body) {
      init.method = "POST";
      init.headers["Content-Type"] = "application/json";
      init.headers["X-Requested-With"] = "coevo-cockpit";
      init.body = JSON.stringify(options.body);
    }
    return fetch(path, init).then(function (response) {
      return response.json().then(function (data) {
        if (response.status === 401) {
          var err = new Error(
            "会话已过期，请使用启动时打印的完整地址重新打开驾驶舱。"
          );
          err.sessionExpired = true;
          throw err;
        }
        return { code: response.status, data: data };
      });
    });
  }

  function setStatus(text, kind) {
    var status = document.getElementById("status");
    status.textContent = text;
    status.classList.toggle("error", kind === "error");
    status.classList.toggle("info", kind === "info");
  }

  function attachTokenForm() {
    var form = document.getElementById("token-form");
    if (form.getAttribute("data-bound") === "1") {
      return;
    }
    form.setAttribute("data-bound", "1");
    var input = document.getElementById("token-input");
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var value = input.value.trim();
      if (!value) {
        input.focus();
        return;
      }
      var button = form.querySelector("button[type=submit]");
      button.disabled = true;
      button.textContent = "验证中…";
      fetch("/api/health", {
        headers: { "X-Cockpit-Token": value },
      }).then(function (response) {
        if (response.status === 200) {
          sessionStorage.setItem("cockpit_token", value);
          location.reload();
          return;
        }
        throw new Error("令牌无效，请检查后重试");
      }).catch(function () {
        button.disabled = false;
        button.textContent = "连接";
        var err = document.getElementById("token-error");
        if (!err) {
          err = el("p", "");
          err.id = "token-error";
          err.className = "error-note";
          form.appendChild(err);
        }
        err.textContent = "令牌无效，请检查后重试";
      });
    });
  }

  function showLoginPanel(message) {
    if (state.refreshTimer) {
      clearInterval(state.refreshTimer);
      state.refreshTimer = null;
    }
    attachTokenForm();
    document.getElementById("status").hidden = true;
    document.getElementById("detail").hidden = true;
    document.getElementById("login-panel").hidden = false;
    var loginMessage = document.getElementById("login-message");
    loginMessage.textContent = message || "";
    loginMessage.hidden = !message;
  }

  function handleAuthError(err) {
    if (err && err.sessionExpired) {
      sessionStorage.removeItem("cockpit_token");
      showLoginPanel("会话已过期，请重新连接。");
      return true;
    }
    return false;
  }

  function el(tag, text) {
    var node = document.createElement(tag);
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  function statusLabel(status) {
    var map = {
      done: "已完成",
      in_progress: "进行中",
      blocked: "受阻",
      pending: "待处理",
      overdue: "已逾期",
    };
    return map[status] || status;
  }

  function statusChip(status) {
    var chip = el("span", statusLabel(status));
    chip.className = "status-chip " + (status || "default");
    return chip;
  }

  function renderTaskRow(task) {
    var item = el("li");
    item.classList.add("task-row");
    var title = el("span", task.title);
    var chip = statusChip(task.status);
    if (isOverdue(task.due_at, false)) {
      chip.classList.add("overdue");
    }
    item.appendChild(title);
    item.appendChild(chip);
    item.addEventListener("click", function () {
      openTaskDetail(task);
    });
    return item;
  }

  function isOverdue(dueAt, completed) {
    if (completed) {
      return false;
    }
    var due = Date.parse(dueAt);
    if (isNaN(due)) {
      return false;
    }
    return due < Date.now();
  }

  function isWpsOpenable(path) {
    var allowed = [".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".rtf", ".pdf"];
    var name = String(path || "").toLowerCase();
    return allowed.some(function (ext) {
      return name.indexOf(ext) === name.length - ext.length;
    });
  }

  function formatBytes(bytes) {
    if (bytes === undefined || bytes === null) {
      return "";
    }
    if (bytes < 1024) {
      return bytes + " B";
    }
    if (bytes < 1024 * 1024) {
      return (bytes / 1024).toFixed(1) + " KB";
    }
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function roleLabel(role) {
    var map = {
      document: "文档",
      feedback: "反馈",
      artifact: "产物",
      dependency: "依赖",
    };
    return map[role] || role || "";
  }

  function showDetail(title) {
    document.getElementById("detail-title").textContent = title;
    document.getElementById("detail").hidden = false;
  }

  function clearNode(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function formatTs(iso) {
    if (!iso) {
      return "";
    }
    var date = new Date(iso);
    if (isNaN(date.getTime())) {
      return iso;
    }
    var pad = function (n) {
      return String(n).padStart(2, "0");
    };
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate())
      + " " + pad(date.getHours()) + ":" + pad(date.getMinutes()) + ":" + pad(date.getSeconds());
  }

  function formatDate(iso) {
    if (!iso) {
      return "-";
    }
    var date = new Date(iso);
    if (isNaN(date.getTime())) {
      return iso;
    }
    var pad = function (n) {
      return String(n).padStart(2, "0");
    };
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate());
  }

  function formatRelative(iso) {
    if (!iso) {
      return "";
    }
    var date = new Date(iso);
    if (isNaN(date.getTime())) {
      return iso;
    }
    var diffMs = Date.now() - date.getTime();
    var diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 60) {
      return "刚刚";
    }
    var diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) {
      return diffMin + " 分钟前";
    }
    var diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) {
      return diffHour + " 小时前";
    }
    var diffDay = Math.floor(diffHour / 24);
    if (diffDay < 7) {
      return diffDay + " 天前";
    }
    return formatTs(iso);
  }

  function formatUptime(seconds) {
    if (!seconds || seconds < 0) {
      return "0 秒";
    }
    var total = Math.floor(seconds);
    var hours = Math.floor(total / 3600);
    var minutes = Math.floor((total % 3600) / 60);
    var secs = total % 60;
    if (hours > 0) {
      return hours + " 小时 " + minutes + " 分";
    }
    if (minutes > 0) {
      return minutes + " 分 " + secs + " 秒";
    }
    return secs + " 秒";
  }

  // ------------------------------------------------------------------
  // 项目列表
  // ------------------------------------------------------------------

  function renderProjects() {
    var list = document.getElementById("project-list");
    var hint = document.getElementById("sidebar-hint");
    var globalPending = document.getElementById("global-pending");
    clearNode(list);
    var pendingCount = state.projects.reduce(function (acc, project) {
      return acc + (project.trace || []).filter(function (step) {
        return step.requires_human_confirmation && !step.confirmed_by;
      }).length;
    }, 0);
    if (globalPending) {
      if (pendingCount > 0) {
        globalPending.textContent = "待确认 " + pendingCount + " 项";
        globalPending.className = "global-pending has-pending";
      } else {
        globalPending.textContent = "无待确认事项";
        globalPending.className = "global-pending clear";
      }
    }
    if (!state.projects.length) {
      list.appendChild(el("li", "暂无项目"));
      if (hint) {
        hint.hidden = false;
      }
      if (globalPending) {
        globalPending.textContent = "";
      }
      return;
    }
    if (hint) {
      hint.hidden = true;
    }
    state.projects.forEach(function (project) {
      var item = el("li");
      item.classList.add("project");
      if (project.project_id === state.activeProjectId) {
        item.classList.add("active");
      }
      var name = el("span", project.display_name || project.project_id);
      name.className = "project-name";
      var id = el("span", project.project_id);
      id.className = "project-id";
      item.appendChild(name);
      item.appendChild(id);
      if (
        project.task_count !== undefined
        || project.milestone_count !== undefined
        || project.artifact_count !== undefined
      ) {
        var counts = el("span");
        counts.className = "project-counts";
        var parts = [];
        if (project.task_count !== undefined) {
          parts.push("任务 " + project.task_count);
        }
        if (project.milestone_count !== undefined) {
          parts.push("里程碑 " + project.milestone_count);
        }
        if (project.artifact_count !== undefined) {
          parts.push("产物 " + project.artifact_count);
        }
        counts.textContent = parts.join(" · ");
        item.appendChild(counts);
      }
      item.addEventListener("click", function () {
        openProject(project.project_id);
      });
      list.appendChild(item);
    });
  }

  function renderProjectSummary(project) {
    var summary = document.getElementById("detail-summary");
    if (!project) {
      summary.textContent = "";
      return;
    }
    var progress = state.milestoneProgress[project.project_id];
    var milestoneText = "里程碑 " + project.milestone_count;
    if (progress && progress.total > 0) {
      milestoneText = "里程碑 " + progress.done + "/" + progress.total;
    }
    summary.textContent =
      "任务 " + project.task_count + " · " + milestoneText +
      " · 产物 " + project.artifact_count;
  }

  function renderPackageSummary(project) {
    var node = document.getElementById("package-summary");
    if (!project || !project.package_path) {
      node.textContent = "";
      return;
    }
    var parts = [];
    parts.push("任务包：" + project.package_path.split(/[\\/]/).pop());
    if (project.package_digest) {
      parts.push("SHA-256 " + project.package_digest.slice(0, 16) + "…");
    }
    if (project.knowledge_bundle_id) {
      parts.push("知识包 " + project.knowledge_bundle_id.slice(0, 24) + "…");
    }
    node.textContent = parts.join(" · ");
  }

  function renderSnapshotTs() {
    var node = document.getElementById("snapshot-ts");
    node.textContent = state.lastSnapshotTs
      ? "数据快照：" + formatTs(state.lastSnapshotTs)
      : "";
  }

  function renderPendingBadge(project) {
    var badge = document.getElementById("pending-badge");
    if (!project || !project.trace || !project.trace.length) {
      badge.hidden = true;
      badge.className = "pending-badge";
      badge.textContent = "";
      return;
    }
    var pending = project.trace.filter(function (step) {
      return step.requires_human_confirmation && !step.confirmed_by;
    }).length;
    var hasConfirmStep = project.trace.some(function (step) {
      return step.requires_human_confirmation;
    });
    if (pending > 0) {
      badge.textContent = "待确认 " + pending;
      badge.className = "pending-badge pending";
      badge.hidden = false;
    } else if (hasConfirmStep) {
      badge.textContent = "无需处理";
      badge.className = "pending-badge ok";
      badge.hidden = false;
    } else {
      badge.hidden = true;
      badge.className = "pending-badge";
      badge.textContent = "";
    }
  }

  function agentLabel(agentId) {
    var map = {
      "agent.task_flow_understanding": "流程理解",
      "agent.task_decomposition": "任务分解",
      "agent.team_recommendation": "团队推荐",
      "agent.task_package_build": "任务包构建",
      "human": "负责人确认",
    };
    return map[agentId] || agentId || "未知";
  }

  function resultLabel(result) {
    var map = {
      ok: "成功",
      skipped: "跳过",
      failed: "失败",
      held: "已挂起",
    };
    return map[result] || result || "";
  }

  function renderTrace(trace) {
    var list = document.getElementById("trace-list");
    clearNode(list);
    if (!trace || !trace.length) {
      list.appendChild(el("li", "暂无编排轨迹"));
      return;
    }
    trace.forEach(function (step) {
      var item = el("li");
      if (step.requires_human_confirmation) {
        item.classList.add(step.confirmed_by ? "confirmed" : "requires-confirm");
      }
      var index = el("span", String(step.step_index + 1));
      index.className = "trace-step";
      var agent = el("span", agentLabel(step.agent_id));
      agent.className = "trace-agent";
      var detail = el("span");
      detail.className = "trace-detail";
      detail.textContent = step.detail
        ? resultLabel(step.result) + " · " + step.detail
        : resultLabel(step.result);
      item.appendChild(index);
      item.appendChild(agent);
      item.appendChild(detail);
      if (step.requires_human_confirmation) {
        var badge = el("span", step.confirmed_by ? "已确认" : "待人工确认");
        badge.className = "trace-badge " + (step.confirmed_by ? "approved" : "pending");
        item.appendChild(badge);
        if (!step.confirmed_by) {
          var confirmBtn = el("button", "确认");
          confirmBtn.addEventListener("click", function () {
            submitPendingAction("confirm");
          });
          var rejectBtn = el("button", "驳回");
          rejectBtn.className = "ghost";
          rejectBtn.addEventListener("click", function () {
            submitPendingAction("reject");
          });
          item.appendChild(confirmBtn);
          item.appendChild(rejectBtn);
        }
      }
      list.appendChild(item);
    });
  }

  function submitPendingAction(action) {
    setStatus(
      action === "confirm" ? "正在确认…" : "正在驳回…",
      "info"
    );
    return api("/api/pending_confirm", {
      body: { action: action },
    }).then(function (result) {
      if (result.code === 200) {
        if (action === "confirm") {
          setStatus("已确认，正在继续执行…", "info");
          waitForConfirmationApplied();
        } else {
          setStatus("已驳回。", "info");
          setTimeout(function () {
            location.reload();
          }, 1200);
        }
        return;
      }
      if (result.code === 503) {
        throw new Error(
          "当前项目无待确认处理器（仅 --serve-gate 演示模式支持网页确认）。"
        );
      }
      throw new Error(result.data.task || result.data.error || "操作失败");
    }).catch(function (err) {
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function waitForConfirmationApplied() {
    var attempts = 0;
    function check() {
      attempts += 1;
      api("/api/list_projects").then(function (result) {
        if (result.code !== 200) {
          throw new Error(result.data.error || "刷新失败");
        }
        var payload = result.data.payload;
        var views = Array.isArray(payload.views) && payload.views.length
          ? payload.views
          : [];
        var project = views.find(function (p) {
          return p.project_id === state.activeProjectId;
        });
        var pending = project && project.trace
          ? project.trace.some(function (step) {
              return step.requires_human_confirmation && !step.confirmed_by;
            })
          : false;
        if (!pending || attempts > 15) {
          location.reload();
          return;
        }
        setTimeout(check, 2000);
      }).catch(function () {
        // 状态暂不可读时稍后重试，最终刷新兜底。
        setTimeout(function () {
          location.reload();
        }, 3000);
      });
    }
    setTimeout(check, 2000);
  }

  function actionLabel(action) {
    var map = {
      "dispatch": "任务下发",
      "confirmation": "人工确认",
      "resume": "恢复编排",
      "package": "任务包处理",
      "recovery": "恢复处理",
      "facade.0": "流程理解",
      "facade.1": "任务分解",
      "facade.2": "团队推荐",
      "facade.3": "人工确认",
      "facade.4": "任务包构建",
      "chain.completed": "编排完成",
      "package.exported": "任务包导出",
      "knowledge.stored": "知识入库",
    };
    return map[action] || action;
  }

  function resultLabelFull(result) {
    var map = {
      attempt: "尝试",
      success: "成功",
      confirmed: "已确认",
      completed: "完成",
      held: "已挂起",
      ok: "成功",
      skipped: "跳过",
      failed: "失败",
    };
    return map[result] || result || "";
  }

  function renderActivity(activity) {
    var list = document.getElementById("activity-list");
    clearNode(list);
    if (!activity || !activity.length) {
      list.appendChild(el("li", "暂无审计动态"));
      return;
    }
    activity.slice(-20).forEach(function (entry) {
      var item = el("li");
      var seq = el("span", "#" + entry.sequence);
      seq.className = "activity-seq";
      var time = el("span", formatRelative(entry.recorded_at));
      time.className = "activity-time";
      time.title = formatTs(entry.recorded_at);
      var action = el("span", actionLabel(entry.action));
      action.className = "activity-action";
      var result = el("span", resultLabelFull(entry.result));
      result.className = "activity-result " + (entry.result || "default");
      var hash = el("span", entry.digest ? entry.digest.slice(0, 8) : "");
      hash.className = "activity-hash";
      item.appendChild(time);
      item.appendChild(seq);
      item.appendChild(action);
      item.appendChild(result);
      item.appendChild(hash);
      list.appendChild(item);
    });
  }

  // ------------------------------------------------------------------
  // 角色切换
  // ------------------------------------------------------------------

  function renderRoleTabs(roles) {
    var nav = document.getElementById("role-tabs");
    clearNode(nav);
    if (!roles.length) {
      var empty = el("span", "暂无角色");
      empty.className = "role-empty";
      nav.appendChild(empty);
      return;
    }
    roles.forEach(function (roleId) {
      var label = state.roleNames[roleId] || roleId;
      if (state.roleCounts[roleId] !== undefined) {
        label += " (" + state.roleCounts[roleId] + ")";
      }
      var button = el("button", label);
      button.setAttribute("data-role-id", roleId);
      if (roleId === state.activeRoleId) {
        button.classList.add("active");
      }
      button.addEventListener("click", function () {
        loadRole(state.activeProjectId, roleId);
      });
      nav.appendChild(button);
    });
  }

  function renderTasks(tasks) {
    var list = document.getElementById("tasks");
    clearNode(list);
    if (!tasks || !tasks.length) {
      list.appendChild(el("li", "暂无任务", "empty-note"));
      return;
    }
    var filtered = tasks.filter(function (task) {
      if (!state.taskFilter) {
        return true;
      }
      return task.status === state.taskFilter;
    });
    if (!filtered.length) {
      list.appendChild(el("li", "没有符合筛选条件的任务", "empty-note"));
      return;
    }
    filtered.slice().sort(function (a, b) {
      var aDue = Date.parse(a.due_at) || Infinity;
      var bDue = Date.parse(b.due_at) || Infinity;
      return aDue - bDue;
    }).forEach(function (task) {
      list.appendChild(renderTaskRow(task));
    });
  }

  function renderMilestones(milestones) {
    var list = document.getElementById("milestones");
    clearNode(list);
    if (!milestones || !milestones.length) {
      list.appendChild(el("li", "暂无里程碑", "empty-note"));
      return;
    }
    milestones.slice().sort(function (a, b) {
      var aDue = Date.parse(a.due_at) || Infinity;
      var bDue = Date.parse(b.due_at) || Infinity;
      return aDue - bDue;
    }).forEach(function (milestone) {
      var item = el("li");
      var overdue = isOverdue(milestone.due_at, milestone.completed);
      var label = milestone.completed ? "（已完成）" : (overdue ? "（已逾期）" : "（进行中）");
      var text = milestone.title + " " + label;
      if (milestone.due_at) {
        text += " · 截止 " + formatDate(milestone.due_at);
      }
      if (milestone.completed) {
        item.classList.add("milestone-done");
      } else if (overdue) {
        item.classList.add("milestone-overdue");
      } else {
        item.classList.add("milestone-open");
      }
      item.appendChild(el("span", text));
      item.classList.add("milestone-row");
      item.addEventListener("click", function () {
        openMilestoneDetail(state.activeProjectId, milestone);
      });
      list.appendChild(item);
    });
  }

  function renderArtifacts(roleView) {
    var list = document.getElementById("artifacts");
    clearNode(list);
    var artifacts = (roleView && roleView.data.payload.artifacts) || [];
    if (!artifacts.length) {
      list.appendChild(el("li", "暂无产物", "empty-note"));
      return;
    }
    artifacts.slice().sort(function (a, b) {
      return String(a.path).localeCompare(String(b.path));
    }).forEach(function (artifact) {
      var item = el("li");
      var main = el("div");
      main.className = "artifact-main";
      var name = el("span", artifact.path);
      name.className = "artifact-name";
      name.title = "点击复制路径";
      name.addEventListener("click", function () {
        copyText(artifact.path);
      });
      var meta = el("span");
      meta.className = "artifact-meta";
      var bits = [];
      var size = formatBytes(artifact.size_bytes);
      if (size) {
        bits.push(size);
      }
      var rl = roleLabel(artifact.role);
      if (rl) {
        bits.push(rl);
      }
      meta.textContent = bits.join(" · ");
      main.appendChild(name);
      if (meta.textContent) {
        main.appendChild(meta);
      }
      item.appendChild(main);
      if (isWpsOpenable(artifact.path)) {
        var button = el("button", "在 WPS 中打开");
        button.addEventListener("click", function () {
          confirmWpsOpen(roleView, artifact);
        });
        item.appendChild(button);
      } else {
        var disabled = el("span", "不支持 WPS 打开");
        disabled.className = "artifact-disabled";
        item.appendChild(disabled);
      }
      list.appendChild(item);
    });
  }

  function renderRole(roleView) {
    renderTasks(roleView.data.payload.current_tasks || []);
    renderMilestones(roleView.data.payload.milestones || []);
    renderArtifacts(roleView);
  }

  // ------------------------------------------------------------------
  // 任务 / 里程碑下钻
  // ------------------------------------------------------------------

  function openTaskDetail(task) {
    var kind = task.milestone_id !== undefined ? "milestone" : "task";
    state.inTaskDetail = true;
    document.getElementById("role-panel").hidden = true;
    document.getElementById("task-detail").hidden = false;
    document.getElementById("task-detail-title").textContent = task.title;
    var body = document.getElementById("task-detail-body");
    clearNode(body);
    if (kind === "milestone") {
      body.appendChild(el("dt", "里程碑编号"));
      body.appendChild(el("dd", task.milestone_id));
      body.appendChild(el("dt", "状态"));
      body.appendChild(el("dd", task.completed ? "已完成" : "进行中"));
    } else {
      body.appendChild(el("dt", "任务编号"));
      body.appendChild(el("dd", task.task_id));
      body.appendChild(el("dt", "状态"));
      body.appendChild(el("dd", statusLabel(task.status)));
    }
    body.appendChild(el("dt", "截止时间"));
    var dueText = formatDate(task.due_at);
    if (isOverdue(task.due_at, false)) {
      dueText += "（已逾期）";
    }
    body.appendChild(el("dd", dueText));
    if (kind === "task") {
      body.appendChild(el("dt", "负责角色"));
      var assignee = state.roleNames[task.assignee_role_id]
        || task.assignee_role_id || "-";
      body.appendChild(el("dd", assignee));
    }
    document.getElementById("task-back").addEventListener("click", closeTaskDetail);
  }

  function openMilestoneDetail(projectId, milestone) {
    setStatus("正在加载里程碑详情…", "info");
    return api("/api/milestone_view?project_id=" + encodeURIComponent(projectId)
      + "&task_id=" + encodeURIComponent(milestone.milestone_id)).then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "里程碑详情加载失败");
      }
      var data = result.data.payload;
      openTaskDetail({
        milestone_id: data.milestone_id,
        title: data.title,
        due_at: data.due_at,
        completed: data.completed,
      });
      setStatus("已连接。", "info");
    }).catch(function (err) {
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function closeTaskDetail() {
    state.inTaskDetail = false;
    document.getElementById("task-detail").hidden = true;
    document.getElementById("role-panel").hidden = false;
  }

  // ------------------------------------------------------------------
  // 数据加载
  // ------------------------------------------------------------------

  function loadRole(projectId, roleId) {
    state.activeRoleId = roleId;
    renderRoleTabs(projectRoles(projectId));
    return api("/api/role_view?project_id=" + encodeURIComponent(projectId)
      + "&role_id=" + encodeURIComponent(roleId)).then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "角色视图加载失败");
      }
      state.roleNames[roleId] = result.data.payload.display_name || roleId;
      state.roleCounts[roleId] = result.data.payload.task_count || 0;
      state.currentTasks = result.data.payload.current_tasks || [];
      var progress = state.milestoneProgress[projectId]
        || { done: 0, total: 0 };
      (result.data.payload.milestones || []).forEach(function (m) {
        progress.total += 1;
        if (m.completed) {
          progress.done += 1;
        }
      });
      state.milestoneProgress[projectId] = progress;
      renderProjectSummary(
        state.projects.find(function (p) {
          return p.project_id === projectId;
        })
      );
      pushHash(projectId, roleId);
      renderRoleTabs(projectRoles(projectId));
      document.getElementById("role-tabs").querySelectorAll("button").forEach(function (button) {
        button.classList.toggle("active", button.getAttribute("data-role-id") === roleId);
      });
      renderRole(result);
      setStatus("已连接。", "info");
      return result;
    }).catch(function (err) {
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function projectRoles(projectId) {
    var project = state.projects.find(function (p) {
      return p.project_id === projectId;
    });
    return project ? (project.roles || []) : [];
  }

  function openProject(projectId) {
    state.activeProjectId = projectId;
    var preservedRole = state.activeRoleId;
    state.activeRoleId = "";
    state.milestoneProgress[projectId] = { done: 0, total: 0 };
    state.currentTasks = [];
    state.taskFilter = "";
    var filter = document.getElementById("task-filter");
    if (filter) {
      filter.value = "";
    }
    state.inTaskDetail = false;
    document.getElementById("task-detail").hidden = true;
    document.getElementById("role-panel").hidden = false;
    var project = state.projects.find(function (p) {
      return p.project_id === projectId;
    });
    renderProjects();
    renderProjectSummary(project);
    renderPackageSummary(project);
    renderPendingBadge(project);
    renderTrace(project ? project.trace : []);
    renderActivity(project ? project.activity : []);
    showDetail(project ? project.display_name : projectId);
    renderRoleTabs(projectRoles(projectId));
    return api("/api/list_roles?project_id=" + encodeURIComponent(projectId)).then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "角色加载失败");
      }
      var roles = result.data.payload.roles || [];
      if (roles.length === 0) {
        renderRoleTabs([]);
        renderTasks([]);
        renderMilestones([]);
        renderArtifacts(null);
        return;
      }
      // 保持当前角色选择；未选择时默认第一个角色。
      var roleId = roles.indexOf(preservedRole) !== -1
        ? preservedRole
        : roles[0];
      pushHash(projectId, roleId);
      return loadRole(projectId, roleId);
    }).catch(function (err) {
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function loadProjects() {
    setStatus("正在加载项目…", "info");
    return api("/api/list_projects").then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "项目加载失败");
      }
      state.lastSnapshotTs = result.data.ts || "";
      applyProjectsPayload(result.data.payload);
      if (state.projects.length === 0) {
        setStatus("暂无项目。", "info");
        document.getElementById("detail").hidden = true;
        return;
      }
      var initial = readHashState();
      if (initial.projectId) {
        var exists = state.projects.some(function (p) {
          return p.project_id === initial.projectId;
        });
        if (exists) {
          state.activeProjectId = initial.projectId;
          if (initial.roleId) {
            state.activeRoleId = initial.roleId;
          }
        }
      }
      if (!state.activeProjectId) {
        state.activeProjectId = state.projects[0].project_id;
      }
      setStatus("已连接。", "info");
      return openProject(state.activeProjectId);
    }).catch(function (err) {
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function loadHealth() {
    return api("/api/health").then(function (result) {
      var node = document.getElementById("health-info");
      if (result.code !== 200) {
        node.textContent = "系统状态不可用";
        return;
      }
      var data = result.data;
      node.textContent =
        "运行 " + formatUptime(data.uptime_sec)
        + " · 会话 " + data.session_count
        + " · 请求 " + data.request_count
        + " · 审计记录 " + data.audit_records
        + (data.log_errors ? " · 日志错误 " + data.log_errors : "");
    }).catch(function () {
      document.getElementById("health-info").textContent = "系统状态不可用";
    });
  }

  function applyProjectsPayload(payload) {
    if (Array.isArray(payload.views) && payload.views.length) {
      state.projects = payload.views;
    } else {
      state.projects = (payload.projects || []).map(function (projectId) {
        return { project_id: projectId, display_name: projectId, roles: [] };
      });
    }
    renderProjects();
    renderSnapshotTs();
  }

  // ------------------------------------------------------------------
  // WPS 打开确认
  // ------------------------------------------------------------------

  function confirmWpsOpen(roleView, artifact) {
    var overlay = el("div");
    overlay.id = "confirm-overlay";
    var dialog = el("div");
    dialog.id = "confirm-dialog";
    dialog.appendChild(el("h3", "打开产物"));
    var p = el("p", "确认在 WPS 中打开文件：");
    p.appendChild(el("br"));
    p.appendChild(el("code", artifact.path));
    dialog.appendChild(p);
    var actions = el("div");
    actions.className = "dialog-actions";
    var cancel = el("button", "取消");
    cancel.className = "ghost";
    var ok = el("button", "确认打开");
    actions.appendChild(cancel);
    actions.appendChild(ok);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    function close() {
      document.body.removeChild(overlay);
    }
    function onKeydown(event) {
      if (event.key === "Escape") {
        close();
        document.removeEventListener("keydown", onKeydown);
      } else if (event.key === "Enter") {
        ok.click();
      }
    }
    cancel.addEventListener("click", function () {
      close();
      document.removeEventListener("keydown", onKeydown);
    });
    document.addEventListener("keydown", onKeydown);
    overlay.addEventListener("click", function (event) {
      if (event.target === overlay) {
        close();
        document.removeEventListener("keydown", onKeydown);
      }
    });
    ok.addEventListener("click", function () {
      close();
      document.removeEventListener("keydown", onKeydown);
      setStatus("正在打开产物…", "info");
      api("/api/wps_open", {
        body: {
          project_id: roleView.data.payload.project_id,
          artifact_path: artifact.path,
          confirm: true,
        },
      }).then(function (result) {
        if (result.code === 200) {
          setStatus("已在 WPS 中打开：" + artifact.path, "info");
        } else {
          var message = result.data.error || result.data.task || "打开失败";
          setStatus(message, "error");
        }
      }).catch(function (err) {
        setStatus(err.message, "error");
      });
    });
  }

  // ------------------------------------------------------------------
  // 刷新
  // ------------------------------------------------------------------

  function refresh() {
    if (state.inFlight) {
      return;
    }
    state.inFlight = true;
    var button = document.getElementById("refresh-btn");
    button.disabled = true;
    var finish = function () {
      button.disabled = false;
      state.inFlight = false;
    };
    api("/api/list_projects").then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "刷新失败");
      }
      state.lastSnapshotTs = result.data.ts || "";
      applyProjectsPayload(result.data.payload);
      // 局部刷新：只重拉当前角色视图，避免整页重载。
      if (state.activeProjectId && state.activeRoleId) {
        return loadRole(state.activeProjectId, state.activeRoleId);
      }
      if (state.activeProjectId) {
        return openProject(state.activeProjectId);
      }
    }).then(finish, function (err) {
      finish();
      if (!handleAuthError(err)) {
        setStatus(err.message, "error");
      }
    });
  }

  function copyCockpitUrl() {
    var url = location.origin + location.pathname;
    if (location.hash) {
      url += location.hash;
    }
    function fallback() {
      var input = document.createElement("textarea");
      input.value = url;
      input.style.position = "fixed";
      input.style.opacity = "0";
      document.body.appendChild(input);
      input.select();
      try {
        document.execCommand("copy");
      } catch (err) {
        setStatus("复制失败，请手动复制地址：" + url, "error");
        document.body.removeChild(input);
        return;
      }
      document.body.removeChild(input);
      setStatus("驾驶舱地址已复制。", "info");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () {
        setStatus("驾驶舱地址已复制。", "info");
      }, fallback);
    } else {
      fallback();
    }
  }

  document.getElementById("refresh-btn").addEventListener("click", refresh);
  document.getElementById("copy-url-btn").addEventListener("click", copyCockpitUrl);
  document.getElementById("task-filter").addEventListener("change", function () {
    state.taskFilter = this.value;
    renderTasks(state.currentTasks);
  });
  document.getElementById("relogin-btn").addEventListener("click", function () {
    sessionStorage.removeItem("cockpit_token");
    showLoginPanel("已退出当前会话，请重新连接。");
  });
  window.addEventListener("hashchange", function () {
    var target = readHashState();
    if (target.projectId && target.projectId !== state.activeProjectId) {
      openProject(target.projectId);
      return;
    }
    if (
      target.projectId === state.activeProjectId
      && target.roleId
      && target.roleId !== state.activeRoleId
    ) {
      loadRole(state.activeProjectId, target.roleId);
    }
  });
  state.refreshTimer = setInterval(function () {
    if (!state.inTaskDetail) {
      refresh();
    }
  }, REFRESH_INTERVAL_MS);

  if (!token) {
    showLoginPanel();
    return;
  }

  function copyText(text) {
    function fallback() {
      var input = document.createElement("textarea");
      input.value = text;
      input.style.position = "fixed";
      input.style.opacity = "0";
      document.body.appendChild(input);
      input.select();
      try {
        document.execCommand("copy");
        setStatus("路径已复制：" + text, "info");
      } catch (err) {
        setStatus("复制失败，请手动复制：" + text, "error");
      }
      document.body.removeChild(input);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        setStatus("路径已复制：" + text, "info");
      }, fallback);
    } else {
      fallback();
    }
  }
  loadProjects();
  loadHealth();
})();
