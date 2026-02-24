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

async function refreshTree() {
  const data = await api("/api/tree");
  $("tree-result").textContent = JSON.stringify(data, null, 2);
}

async function runTreeSearch() {
  const pattern = $("tree-search-input").value.trim();
  if (!pattern) return;
  const data = await api(`/api/search?pattern=${encodeURIComponent(pattern)}`);
  $("tree-search-result").textContent = JSON.stringify(data, null, 2);
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

  $("tree-refresh-btn").onclick = refreshTree;
  $("tree-search-btn").onclick = runTreeSearch;
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
