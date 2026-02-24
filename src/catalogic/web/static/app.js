const $ = (id) => document.getElementById(id);
const API_BASE = window.CATALOGIC_API_BASE || "";
let pickerCurrentPath = null;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

function switchTab(tabId) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === tabId);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${tabId}`);
  });
}

async function refreshRoots() {
  const roots = await api("/api/roots");
  const ul = $("roots-list");
  ul.innerHTML = "";
  roots.forEach((root) => {
    const li = document.createElement("li");
    li.textContent = `${root.id}: ${root.path} `;
    const del = document.createElement("button");
    del.textContent = "Удалить";
    del.onclick = async () => {
      await api(`/api/roots/${root.id}`, { method: "DELETE" });
      await refreshRoots();
    };
    li.appendChild(del);
    ul.appendChild(li);
  });
}

async function openDirPicker(startPath = null) {
  $("dir-picker").classList.remove("hidden");
  await loadDirPicker(startPath);
}

function closeDirPicker() {
  $("dir-picker").classList.add("hidden");
}

async function loadDirPicker(path = null) {
  const query = path ? `?path=${encodeURIComponent(path)}` : "";
  const data = await api(`/api/fs/list-dirs${query}`);
  pickerCurrentPath = data.current_path;
  $("picker-current-path").textContent = data.current_path;

  const list = $("picker-list");
  list.innerHTML = "";
  data.dirs.forEach((dir) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.textContent = dir.name;
    btn.onclick = () => loadDirPicker(dir.path);
    li.appendChild(btn);
    list.appendChild(li);
  });

  const upBtn = $("picker-up-btn");
  upBtn.disabled = !data.parent_path;
  upBtn.onclick = () => {
    if (data.parent_path) loadDirPicker(data.parent_path);
  };
}

async function refreshStatus() {
  const status = await api("/api/scan/status");
  const worker = status.worker_alive ? "alive" : "offline";
  const stale =
    status.worker_stale_sec === null || status.worker_stale_sec === undefined
      ? "n/a"
      : `${Number(status.worker_stale_sec).toFixed(1)}s`;
  $("scan-status").textContent =
    `status: ${status.state} (desired: ${status.desired_state}), worker: ${worker} [stale=${stale}], processed: ${status.processed_files}, emitted: ${status.emitted_records}, skipped: ${status.skipped_files}`;

  const startBtn = $("start-scan-btn");
  const stopBtn = $("stop-scan-btn");
  const warning = $("worker-warning");
  const workerAlive = Boolean(status.worker_alive);

  startBtn.disabled = !workerAlive;
  stopBtn.disabled = status.state !== "running" && status.desired_state !== "running";
  warning.classList.toggle("hidden", workerAlive);
}

function formatSize(size) {
  const value = Number(size);
  if (!Number.isFinite(value) || value < 0) return "?";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 * 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function createFileNode(item) {
  const row = document.createElement("div");
  row.className = "tree-node";

  const spacer = document.createElement("span");
  spacer.textContent = " ";
  spacer.style.display = "inline-block";
  spacer.style.width = "26px";
  row.appendChild(spacer);

  const label = document.createElement("span");
  label.textContent = `${item.name} (${formatSize(item.size)})`;
  row.appendChild(label);
  return row;
}

function renderTreeChildren(container, items, rootId) {
  container.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("div");
    empty.textContent = "Пусто";
    container.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    if (item.type === "dir") {
      container.appendChild(createDirNode(item, rootId));
      return;
    }
    container.appendChild(createFileNode(item));
  });
}

function createDirNode(item, rootId) {
  const wrapper = document.createElement("div");

  const row = document.createElement("div");
  row.className = "tree-node";
  wrapper.appendChild(row);

  const toggle = document.createElement("button");
  toggle.textContent = ">";
  row.appendChild(toggle);

  const name = document.createElement("span");
  name.className = "tree-name";
  name.textContent = item.name;
  row.appendChild(name);

  const children = document.createElement("div");
  children.className = "tree-children hidden";
  wrapper.appendChild(children);

  let loaded = false;
  let expanded = false;

  const toggleOpen = async () => {
    if (!loaded) {
      toggle.disabled = true;
      try {
        const query = new URLSearchParams({
          root_id: String(rootId),
          dir_path: item.path,
        });
        const data = await api(`/api/tree/children?${query.toString()}`);
        renderTreeChildren(children, data.children || [], rootId);
        loaded = true;
      } finally {
        toggle.disabled = false;
      }
    }
    expanded = !expanded;
    children.classList.toggle("hidden", !expanded);
    toggle.textContent = expanded ? "v" : ">";
  };

  toggle.onclick = () => {
    toggleOpen().catch((err) => alert(`Load tree node failed: ${err.message}`));
  };
  name.onclick = toggle.onclick;

  return wrapper;
}

async function refreshTree() {
  const roots = await api("/api/roots");
  const container = $("tree-result");
  container.innerHTML = "";
  if (!roots.length) {
    container.textContent = "Нет добавленных путей сканирования.";
    return;
  }

  roots.forEach((root) => {
    const rootNode = createDirNode(
      {
        name: `[${root.id}] ${root.path}`,
        path: root.path,
        type: "dir",
      },
      root.id
    );
    container.appendChild(rootNode);
  });
}

async function runTreeSearch() {
  const pattern = $("tree-search-input").value.trim();
  if (!pattern) return;
  const data = await api(`/api/search?pattern=${encodeURIComponent(pattern)}`);
  const box = $("tree-search-result");
  box.innerHTML = "";
  const items = data.items || [];
  if (!items.length) {
    box.textContent = "Ничего не найдено.";
    return;
  }

  const ul = document.createElement("ul");
  ul.className = "search-list";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.path} (${formatSize(item.size)})`;
    ul.appendChild(li);
  });
  box.appendChild(ul);
}

async function refreshDuplicates() {
  const data = await api("/api/duplicates");
  $("dups-result").textContent = JSON.stringify(data, null, 2);
}

function bindActions() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.onclick = () => switchTab(tab.dataset.tab);
  });

  $("add-root-btn").onclick = async () => {
    const path = $("root-input").value.trim();
    if (!path) return;
    await api("/api/roots", {
      method: "POST",
      body: JSON.stringify({ path }),
    });
    $("root-input").value = "";
    await refreshRoots();
  };

  $("open-picker-btn").onclick = async () => {
    try {
      const raw = $("root-input").value.trim();
      await openDirPicker(raw || null);
    } catch (err) {
      alert(`Directory picker failed: ${err.message}`);
    }
  };
  $("picker-close-btn").onclick = closeDirPicker;
  $("picker-select-btn").onclick = () => {
    if (pickerCurrentPath) {
      $("root-input").value = pickerCurrentPath;
    }
    closeDirPicker();
  };

  $("start-scan-btn").onclick = async () => {
    try {
      await api("/api/scan/start", {
        method: "POST",
        body: JSON.stringify({}),
      });
    } catch (err) {
      alert(`Start failed: ${err.message}`);
    }
    await refreshStatus();
  };

  $("stop-scan-btn").onclick = async () => {
    try {
      await api("/api/scan/stop", { method: "POST" });
    } catch (err) {
      alert(`Stop failed: ${err.message}`);
    }
    await refreshStatus();
  };

  $("tree-refresh-btn").onclick = async () => {
    try {
      await refreshTree();
    } catch (err) {
      alert(`Refresh tree failed: ${err.message}`);
    }
  };
  $("tree-search-btn").onclick = async () => {
    try {
      await runTreeSearch();
    } catch (err) {
      alert(`Search failed: ${err.message}`);
    }
  };
  $("dups-refresh-btn").onclick = refreshDuplicates;
}

async function bootstrap() {
  bindActions();
  await refreshRoots();
  await refreshStatus();
  await refreshTree();
  await refreshDuplicates();
  setInterval(() => {
    refreshStatus().catch(() => {});
  }, 2000);
}

bootstrap().catch((err) => {
  console.error(err);
  alert(`UI init failed: ${err.message}`);
});
