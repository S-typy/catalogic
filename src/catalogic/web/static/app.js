const $ = (id) => document.getElementById(id);
const API_BASE = window.CATALOGIC_API_BASE || "";
const PANEL_WIDTH_STORAGE_KEY = "catalogic_tree_left_panel_width";

let pickerCurrentPath = null;
const treeCache = new Map();
const fileDetailsCache = new Map();
let selectedDirKey = null;
let selectedDirContext = null;
let selectedFilePath = null;
let currentFiles = [];
const fileSort = { key: "name", direction: "asc" };

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

function initBrowserPaneResize() {
  const layout = $("browser-layout");
  const resizer = $("pane-resizer");
  if (!layout || !resizer) {
    return;
  }

  const applyWidth = (rawWidth) => {
    const containerWidth = layout.clientWidth;
    if (!Number.isFinite(rawWidth) || containerWidth <= 0) {
      return null;
    }
    const minWidth = 220;
    const maxWidth = Math.max(minWidth, containerWidth - 320);
    const clamped = Math.min(Math.max(rawWidth, minWidth), maxWidth);
    layout.style.setProperty("--left-pane-width", `${Math.round(clamped)}px`);
    return clamped;
  };

  const savedWidth = Number(window.localStorage.getItem(PANEL_WIDTH_STORAGE_KEY));
  if (Number.isFinite(savedWidth) && savedWidth > 0) {
    applyWidth(savedWidth);
  }

  resizer.addEventListener("pointerdown", (event) => {
    if (window.matchMedia("(max-width: 900px)").matches) {
      return;
    }
    event.preventDefault();
    const rect = layout.getBoundingClientRect();
    layout.classList.add("resizing");
    resizer.setPointerCapture(event.pointerId);

    const updateWidth = (clientX) => {
      const nextWidth = clientX - rect.left;
      const applied = applyWidth(nextWidth);
      if (applied !== null) {
        window.localStorage.setItem(PANEL_WIDTH_STORAGE_KEY, String(applied));
      }
    };

    const onMove = (moveEvent) => {
      updateWidth(moveEvent.clientX);
    };

    const onEnd = (endEvent) => {
      layout.classList.remove("resizing");
      if (resizer.hasPointerCapture(endEvent.pointerId)) {
        resizer.releasePointerCapture(endEvent.pointerId);
      }
      resizer.removeEventListener("pointermove", onMove);
      resizer.removeEventListener("pointerup", onEnd);
      resizer.removeEventListener("pointercancel", onEnd);
    };

    resizer.addEventListener("pointermove", onMove);
    resizer.addEventListener("pointerup", onEnd);
    resizer.addEventListener("pointercancel", onEnd);
  });

  window.addEventListener("resize", () => {
    const current = Number.parseFloat(getComputedStyle(layout).getPropertyValue("--left-pane-width"));
    if (Number.isFinite(current)) {
      applyWidth(current);
    }
  });
}

function treeKey(rootId, path) {
  return `${String(rootId)}:${path}`;
}

function normalizePath(path) {
  if (!path) {
    return "/";
  }
  if (path === "/") {
    return "/";
  }
  return String(path).replace(/\/+$/, "");
}

function getParentPath(path) {
  const normalized = normalizePath(path);
  if (normalized === "/") {
    return "/";
  }
  const idx = normalized.lastIndexOf("/");
  if (idx <= 0) {
    return "/";
  }
  return normalized.slice(0, idx);
}

function isInsideRoot(path, rootPath) {
  const normalizedPath = normalizePath(path);
  const normalizedRoot = normalizePath(rootPath);
  if (normalizedRoot === "/") {
    return normalizedPath.startsWith("/");
  }
  return normalizedPath === normalizedRoot || normalizedPath.startsWith(`${normalizedRoot}/`);
}

function setFilesSelectionInfo(text) {
  const info = $("files-selection-info");
  if (info) {
    info.textContent = text;
  }
}

function setFileDetailsPlaceholder(text) {
  const panel = $("file-details-panel");
  if (panel) {
    panel.textContent = text;
  }
}

function formatSize(size) {
  const value = Number(size);
  if (!Number.isFinite(value) || value < 0) return "?";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 * 1024 * 1024) return `${(value / (1024 * 1024)).toFixed(1)} MB`;
  return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function formatDateTime(epochSec) {
  const value = Number(epochSec);
  if (!Number.isFinite(value) || value <= 0) return "-";
  const date = new Date(value * 1000);
  return date.toLocaleString();
}

function splitChildren(payload) {
  if (Array.isArray(payload.children)) {
    return {
      dirs: payload.children.filter((item) => item.type === "dir"),
      files: payload.children.filter((item) => item.type === "file"),
    };
  }
  return { dirs: [], files: [] };
}

async function getDirData(rootId, dirPath, force = false) {
  const key = treeKey(rootId, dirPath);
  if (!force && treeCache.has(key)) {
    return treeCache.get(key);
  }

  const query = new URLSearchParams({
    root_id: String(rootId),
    dir_path: dirPath,
  });
  const payload = await api(`/api/tree/children?${query.toString()}`);
  const split = splitChildren(payload);
  const data = {
    rootId: Number(payload.root_id || rootId),
    rootPath: payload.root_path || dirPath,
    dirPath: payload.dir_path || dirPath,
    dirs: split.dirs,
    files: split.files,
  };
  treeCache.set(key, data);
  return data;
}

function refreshDirectorySelectionHighlight() {
  document.querySelectorAll(".tree-name").forEach((node) => {
    const key = node.dataset.dirKey;
    node.classList.toggle("selected", key === selectedDirKey);
  });
}

function sortedFiles(files) {
  const key = fileSort.key;
  const dir = fileSort.direction === "asc" ? 1 : -1;
  const sorted = [...files];
  sorted.sort((a, b) => {
    if (key === "size") {
      const av = Number.isFinite(Number(a.size)) ? Number(a.size) : -1;
      const bv = Number.isFinite(Number(b.size)) ? Number(b.size) : -1;
      return (av - bv) * dir;
    }
    if (key === "mtime") {
      const av = Number.isFinite(Number(a.mtime)) ? Number(a.mtime) : -1;
      const bv = Number.isFinite(Number(b.mtime)) ? Number(b.mtime) : -1;
      return (av - bv) * dir;
    }
    return String(a.name || "").localeCompare(String(b.name || ""), "ru", { sensitivity: "base" }) * dir;
  });
  return sorted;
}

function updateSortButtons() {
  const labels = {
    name: "Имя",
    size: "Размер",
    mtime: "Дата изменения",
  };
  const arrow = fileSort.direction === "asc" ? "↑" : "↓";
  $("sort-name-btn").textContent = `${labels.name}${fileSort.key === "name" ? ` ${arrow}` : ""}`;
  $("sort-size-btn").textContent = `${labels.size}${fileSort.key === "size" ? ` ${arrow}` : ""}`;
  $("sort-mtime-btn").textContent = `${labels.mtime}${fileSort.key === "mtime" ? ` ${arrow}` : ""}`;
}

function toMetaText(meta) {
  if (!meta || typeof meta !== "object") {
    return "n/a";
  }
  return JSON.stringify(meta, null, 2);
}

function renderFileDetails(details) {
  const panel = $("file-details-panel");
  if (!panel) {
    return;
  }
  if (!details) {
    panel.textContent = "Нет данных по выбранному файлу.";
    return;
  }

  panel.innerHTML = "";
  const grid = document.createElement("div");
  grid.className = "file-details-grid";

  const addPair = (key, value) => {
    const keyNode = document.createElement("div");
    keyNode.className = "file-details-key";
    keyNode.textContent = key;
    grid.appendChild(keyNode);

    const valueNode = document.createElement("div");
    valueNode.className = "file-details-value";
    valueNode.textContent = value;
    grid.appendChild(valueNode);
  };

  addPair("Путь", details.path || "-");
  addPair("Имя", details.name || "-");
  addPair("Размер", `${formatSize(details.size)} (${Number(details.size || 0)} B)`);
  addPair("Дата изменения", formatDateTime(details.mtime));
  addPair("Дата создания", formatDateTime(details.ctime));
  addPair("MIME", details.mime || "-");
  addPair("Символическая ссылка", details.is_symlink ? "Да" : "Нет");
  addPair("MD5", details.md5 || "n/a");

  const sections = [
    { title: "Video metadata", payload: details.video_meta },
    { title: "Audio metadata", payload: details.audio_meta },
    { title: "Image metadata", payload: details.image_meta },
  ];

  sections.forEach((section) => {
    const wrap = document.createElement("div");
    wrap.className = "file-details-meta";
    const title = document.createElement("strong");
    title.textContent = section.title;
    wrap.appendChild(title);
    const pre = document.createElement("pre");
    pre.textContent = toMetaText(section.payload);
    wrap.appendChild(pre);
    grid.appendChild(wrap);
  });

  panel.appendChild(grid);
}

async function getFileDetails(rootId, path, force = false) {
  const key = `${String(rootId)}:${path}`;
  if (!force && fileDetailsCache.has(key)) {
    return fileDetailsCache.get(key);
  }
  const query = new URLSearchParams({ root_id: String(rootId), path });
  const payload = await api(`/api/file/details?${query.toString()}`);
  fileDetailsCache.set(key, payload);
  return payload;
}

async function loadAndRenderFileDetails(rootId, path) {
  setFileDetailsPlaceholder("Загрузка информации о файле...");
  const details = await getFileDetails(rootId, path);
  if (selectedFilePath !== path) {
    return;
  }
  renderFileDetails(details);
}

function scrollSelectedFileIntoView() {
  if (!selectedFilePath) {
    return;
  }
  const body = $("files-table-body");
  if (!body) {
    return;
  }
  const rows = body.querySelectorAll("tr[data-file-path]");
  rows.forEach((row) => {
    if (row.dataset.filePath === selectedFilePath) {
      row.scrollIntoView({ block: "nearest" });
    }
  });
}

function getSortedCurrentFiles() {
  return sortedFiles(currentFiles);
}

function selectFileByIndex(index, { ensureVisible = true } = {}) {
  const rows = getSortedCurrentFiles();
  if (!rows.length) {
    return;
  }
  const clamped = Math.min(Math.max(index, 0), rows.length - 1);
  const item = rows[clamped];
  selectedFilePath = item.path;
  setFilesSelectionInfo(`Выбран файл: ${item.path}`);
  renderFilesTable();
  if (selectedDirContext) {
    loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
      setFileDetailsPlaceholder("Не удалось загрузить детальную информацию о файле.");
    });
  }
  if (ensureVisible) {
    scrollSelectedFileIntoView();
  }
}

function moveFileSelection(step) {
  const rows = getSortedCurrentFiles();
  if (!rows.length) {
    return;
  }
  const currentIndex = rows.findIndex((item) => item.path === selectedFilePath);
  const start = currentIndex >= 0 ? currentIndex : step > 0 ? -1 : rows.length;
  selectFileByIndex(start + step);
}

function tryCopyToClipboard(text) {
  if (!text) {
    return Promise.resolve(false);
  }

  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard
      .writeText(text)
      .then(() => true)
      .catch(() => false);
  }

  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  const ok = document.execCommand("copy");
  document.body.removeChild(ta);
  return Promise.resolve(ok);
}

async function activateSelectedFile() {
  if (!selectedFilePath) {
    return;
  }
  const item = currentFiles.find((file) => file.path === selectedFilePath);
  if (!item) {
    return;
  }
  await activateFile(item);
}

async function navigateToParentDirectory() {
  if (!selectedDirContext) {
    setFilesSelectionInfo("Сначала выберите каталог в дереве.");
    return;
  }
  const currentPath = normalizePath(selectedDirContext.dirPath);
  const rootPath = normalizePath(selectedDirContext.rootPath);
  if (currentPath === rootPath) {
    setFilesSelectionInfo("Вы уже в корневом каталоге.");
    return;
  }

  const parentPath = normalizePath(getParentPath(currentPath));
  const targetPath = isInsideRoot(parentPath, rootPath) ? parentPath : rootPath;
  await selectDirectory(selectedDirContext.rootId, targetPath, targetPath);
  setFilesSelectionInfo(`Каталог: ${targetPath}`);
}

async function activateFile(item) {
  if (!item) {
    return;
  }
  selectedFilePath = item.path;
  renderFilesTable();
  const copied = await tryCopyToClipboard(item.path);
  if (copied) {
    setFilesSelectionInfo(`Путь скопирован: ${item.path}`);
  } else {
    setFilesSelectionInfo(`Файл выбран: ${item.path}`);
  }
}

function renderFilesTable() {
  const body = $("files-table-body");
  body.innerHTML = "";

  if (selectedFilePath && !currentFiles.some((item) => item.path === selectedFilePath)) {
    selectedFilePath = null;
  }

  const rows = sortedFiles(currentFiles);
  if (!rows.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.textContent = "Файлы в каталоге не найдены.";
    tr.appendChild(td);
    body.appendChild(tr);
    updateSortButtons();
    return;
  }

  rows.forEach((item) => {
    const tr = document.createElement("tr");
    tr.dataset.filePath = item.path;
    if (item.path === selectedFilePath) {
      tr.classList.add("selected");
    }
    tr.onclick = () => {
      selectedFilePath = item.path;
      setFilesSelectionInfo(`Выбран файл: ${item.path}`);
      renderFilesTable();
      if (selectedDirContext) {
        loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
          setFileDetailsPlaceholder("Не удалось загрузить детальную информацию о файле.");
        });
      }
    };
    tr.ondblclick = () => {
      activateFile(item).catch(() => {
        setFilesSelectionInfo(`Файл выбран: ${item.path}`);
      });
    };

    const name = document.createElement("td");
    name.textContent = item.name;
    tr.appendChild(name);

    const size = document.createElement("td");
    size.textContent = formatSize(item.size);
    tr.appendChild(size);

    const mtime = document.createElement("td");
    mtime.textContent = formatDateTime(item.mtime);
    tr.appendChild(mtime);

    body.appendChild(tr);
  });
  updateSortButtons();
}

function setFileSort(key) {
  if (fileSort.key === key) {
    fileSort.direction = fileSort.direction === "asc" ? "desc" : "asc";
  } else {
    fileSort.key = key;
    fileSort.direction = "asc";
  }
  renderFilesTable();
}

async function selectDirectory(rootId, dirPath, title) {
  const data = await getDirData(rootId, dirPath);
  selectedDirContext = {
    rootId: Number(rootId),
    rootPath: normalizePath(data.rootPath || dirPath),
    dirPath: normalizePath(data.dirPath || dirPath),
  };
  selectedDirKey = treeKey(rootId, selectedDirContext.dirPath);
  selectedFilePath = null;
  currentFiles = data.files || [];
  $("files-title").textContent = `Файлы: ${title || dirPath}`;
  setFilesSelectionInfo("Выберите файл для действий.");
  setFileDetailsPlaceholder("Выберите файл в таблице, чтобы посмотреть полную информацию.");
  renderFilesTable();
  refreshDirectorySelectionHighlight();
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
  name.dataset.dirKey = treeKey(rootId, item.path);
  name.tabIndex = 0;
  name.textContent = item.name;
  row.appendChild(name);

  const children = document.createElement("div");
  children.className = "tree-children hidden";
  wrapper.appendChild(children);

  let loaded = false;
  let expanded = false;

  const expand = async () => {
    if (!loaded) {
      toggle.disabled = true;
      try {
        const data = await getDirData(rootId, item.path);
        children.innerHTML = "";
        const dirs = data.dirs || [];
        if (!dirs.length) {
          toggle.disabled = true;
          toggle.textContent = "·";
          loaded = true;
          return;
        }
        dirs.forEach((dir) => children.appendChild(createDirNode(dir, rootId)));
        loaded = true;
      } finally {
        if (toggle.textContent !== "·") {
          toggle.disabled = false;
        }
      }
    }
    expanded = !expanded;
    children.classList.toggle("hidden", !expanded);
    toggle.textContent = expanded ? "v" : ">";
  };

  toggle.onclick = () => {
    if (toggle.textContent === "·") return;
    expand().catch((err) => alert(`Load tree node failed: ${err.message}`));
  };

  name.onclick = () => {
    selectDirectory(rootId, item.path, item.path).catch((err) => {
      alert(`Open directory failed: ${err.message}`);
    });
  };

  name.ondblclick = () => {
    selectDirectory(rootId, item.path, item.path).catch((err) => {
      alert(`Open directory failed: ${err.message}`);
    });
    if (toggle.textContent !== "·") {
      expand().catch((err) => alert(`Load tree node failed: ${err.message}`));
    }
  };

  name.onkeydown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      event.stopPropagation();
      name.onclick();
      return;
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      event.stopPropagation();
      if (!expanded && toggle.textContent !== "·") {
        expand().catch((err) => alert(`Load tree node failed: ${err.message}`));
      }
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      event.stopPropagation();
      if (expanded && toggle.textContent !== "·") {
        expand().catch((err) => alert(`Load tree node failed: ${err.message}`));
      }
    }
  };

  return wrapper;
}

async function refreshTree() {
  const roots = await api("/api/roots");
  treeCache.clear();
  fileDetailsCache.clear();
  selectedDirKey = null;
  selectedDirContext = null;
  selectedFilePath = null;
  currentFiles = [];
  $("files-title").textContent = "Файлы";
  setFilesSelectionInfo("Выберите файл для действий.");
  setFileDetailsPlaceholder("Выберите файл в таблице, чтобы посмотреть полную информацию.");
  renderFilesTable();

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
      await refreshTree();
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

function bindActions() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.onclick = () => switchTab(tab.dataset.tab);
  });

  $("sort-name-btn").onclick = () => setFileSort("name");
  $("sort-size-btn").onclick = () => setFileSort("size");
  $("sort-mtime-btn").onclick = () => setFileSort("mtime");

  $("add-root-btn").onclick = async () => {
    const path = $("root-input").value.trim();
    if (!path) return;
    await api("/api/roots", {
      method: "POST",
      body: JSON.stringify({ path }),
    });
    $("root-input").value = "";
    await refreshRoots();
    await refreshTree();
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

  document.addEventListener("keydown", (event) => {
    const treeTab = $("tab-tree");
    if (!treeTab || !treeTab.classList.contains("active")) {
      return;
    }
    const target = event.target;
    const inEditable =
      target instanceof HTMLElement &&
      (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
    if (inEditable) {
      return;
    }
    const inTree = target instanceof HTMLElement && Boolean(target.closest("#tree-result"));
    const isCopyHotkey =
      (event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === "c";
    if (inTree && event.key !== "Backspace" && !isCopyHotkey) {
      return;
    }

    if (isCopyHotkey) {
      event.preventDefault();
      if (!selectedFilePath) {
        setFilesSelectionInfo("Сначала выберите файл.");
        return;
      }
      activateSelectedFile().catch(() => {
        setFilesSelectionInfo("Не удалось скопировать путь файла.");
      });
      return;
    }

    if (event.key === "Backspace") {
      event.preventDefault();
      navigateToParentDirectory().catch(() => {
        setFilesSelectionInfo("Не удалось перейти в родительский каталог.");
      });
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveFileSelection(1);
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveFileSelection(-1);
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      selectFileByIndex(0);
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      selectFileByIndex(Number.MAX_SAFE_INTEGER);
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      activateSelectedFile().catch(() => {
        setFilesSelectionInfo("Не удалось обработать выбранный файл.");
      });
    }
  });
}

async function bootstrap() {
  initBrowserPaneResize();
  bindActions();
  updateSortButtons();
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
