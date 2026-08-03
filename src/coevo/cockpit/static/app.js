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
        return { code: response.status, data: data };
      });
    });
  }

  function setStatus(text, isError) {
    var status = document.getElementById("status");
    status.textContent = text;
    status.classList.toggle("error", !!isError);
  }

  function el(tag, text) {
    var node = document.createElement(tag);
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  function showDetail(title) {
    document.getElementById("detail-title").textContent = title;
    document.getElementById("detail").hidden = false;
  }

  function renderRoles(roleView) {
    var container = document.getElementById("roles");
    container.textContent = "";
    container.appendChild(el("h3", "Roles"));
    var list = el("ul");
    var role = el("li", roleView.data.payload.display_name + " (" + roleView.data.payload.role_id + ")");
    role.appendChild(el("span", " - " + roleView.data.payload.task_count + " tasks"));
    list.appendChild(role);
    container.appendChild(list);
  }

  function renderTasks(roleView) {
    var list = document.getElementById("tasks");
    list.textContent = "";
    (roleView.data.payload.tasks || []).forEach(function (task) {
      var item = el("li", task.title + " [" + task.status + "] due " + task.due_at);
      list.appendChild(item);
    });
  }

  function renderMilestones(roleView) {
    var list = document.getElementById("milestones");
    list.textContent = "";
    (roleView.data.payload.milestones || []).forEach(function (milestone) {
      var item = el("li", milestone.title + (milestone.completed ? " (done)" : " (open)"));
      list.appendChild(item);
    });
  }

  function renderArtifacts(roleView) {
    var list = document.getElementById("artifacts");
    list.textContent = "";
    (roleView.data.payload.artifacts || []).forEach(function (artifact) {
      var item = el("li", artifact.path);
      var button = el("button", "Open in WPS");
      button.addEventListener("click", function () {
        api("/api/wps_open", {
          body: { project_id: roleView.data.payload.project_id, artifact_path: artifact.path, confirm: true },
        }).then(function (result) {
          setStatus(result.data.task || "WPS request accepted", result.code !== 200);
        });
      });
      item.appendChild(button);
      list.appendChild(item);
    });
  }

  function loadRole(projectId, roleId) {
    return api("/api/role_view?project_id=" + encodeURIComponent(projectId)
      + "&role_id=" + encodeURIComponent(roleId)).then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "role view failed");
      }
      return result;
    });
  }

  function openProject(projectId, displayName) {
    showDetail(displayName + " (" + projectId + ")");
    document.getElementById("roles").textContent = "Loading roles?";
    return api("/api/list_roles?project_id=" + encodeURIComponent(projectId)).then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "roles failed");
      }
      var roles = result.data.payload.roles || [];
      if (roles.length === 0) {
        document.getElementById("roles").textContent = "No roles.";
        return;
      }
      var first = roles[0];
      return loadRole(projectId, first).then(function (roleView) {
        renderRoles(roleView);
        renderTasks(roleView);
        renderMilestones(roleView);
        renderArtifacts(roleView);
      });
    }).catch(function (err) {
      setStatus(err.message, true);
    });
  }

  function loadProjects() {
    var list = document.getElementById("project-list");
    list.textContent = "";
    setStatus("Loading projects?");
    return api("/api/list_projects").then(function (result) {
      if (result.code !== 200) {
        throw new Error(result.data.error || "list failed");
      }
      setStatus("Connected.");
      var projects = result.data.payload.projects || [];
      if (projects.length === 0) {
        list.appendChild(el("li", "(no projects)"));
        return;
      }
      projects.forEach(function (projectId) {
        var item = el("li", projectId);
        item.classList.add("project");
        item.addEventListener("click", function () {
          openProject(projectId, projectId);
        });
        list.appendChild(item);
      });
    }).catch(function (err) {
      setStatus(err.message, true);
    });
  }

  if (!token) {
    setStatus("No session token. Start the cockpit with ?token=?", true);
    return;
  }
  loadProjects();
})();
