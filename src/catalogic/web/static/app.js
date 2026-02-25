const $ = (id) => document.getElementById(id);
const API_BASE = window.CATALOGIC_API_BASE || "";
const LEFT_PANEL_WIDTH_STORAGE_KEY = "catalogic_tree_left_panel_width";
const DETAILS_PANEL_WIDTH_STORAGE_KEY = "catalogic_tree_details_panel_width";
const LANG_STORAGE_KEY = "catalogic_ui_language";

const I18N = {
  ru: {
    app_title: "Catalogic STEP1",
    worker_warning: "Сканер недоступен. Запустите сервис `catalogic-scanner`.",
    tab_settings: "Настройки",
    tab_tree: "Просмотр дерева",
    tab_state: "Состояние",
    tab_duplicates: "Поиск дубликатов",
    settings_title: "Настройки",
    settings_language_label: "Язык интерфейса:",
    language_ru: "Русский",
    language_en: "English",
    root_input_placeholder: "/mnt/storage/media",
    open_picker_btn: "Выбрать каталог",
    add_root_btn: "Добавить путь",
    picker_up_btn: "Вверх",
    picker_select_btn: "Выбрать текущий",
    picker_close_btn: "Закрыть",
    scan_mode_label: "Режим сканирования:",
    scan_mode_add_new: "Добавление новых",
    scan_mode_rebuild: "Пересоздание базы",
    follow_symlinks_label: "Следовать symlink-директориям:",
    start_scan_btn: "Старт сканера",
    stop_scan_btn: "Стоп сканера",
    tree_title: "Просмотр дерева",
    tree_search_placeholder: "Поиск по имени (*, ?)",
    tree_search_btn: "Искать",
    tree_refresh_btn: "Обновить дерево",
    tree_dirs_title: "Каталоги",
    files_title: "Файлы",
    files_select_dir_left: "Выберите каталог слева.",
    files_selection_default: "Выберите файл для действий.",
    file_details_title: "Детали файла",
    file_details_placeholder: "Выберите файл в таблице, чтобы посмотреть полную информацию.",
    state_title: "Состояние",
    state_refresh_btn: "Обновить",
    state_scan: "Сканер",
    state_worker_process: "Процесс worker",
    state_metrics: "Метрики",
    state_utilities: "Утилиты",
    dups_title: "Поиск дубликатов (имя + размер)",
    dups_refresh_btn: "Обновить",
    delete_root_btn: "Удалить",
    pane_resize_title: "Изменить размер панелей",
    sort_name: "Имя",
    sort_size: "Размер",
    sort_mtime: "Дата изменения",
    yes: "Да",
    no: "Нет",
    na: "n/a",
    unknown: "неизвестно",
    loading_file_details: "Загрузка информации о файле...",
    no_file_data: "Нет данных по выбранному файлу.",
    file_details_error: "Не удалось загрузить детальную информацию о файле.",
    file_details_path: "Путь",
    file_details_name: "Имя",
    file_details_size: "Размер",
    file_details_mtime: "Дата изменения",
    file_details_ctime: "Дата создания",
    file_details_mime: "MIME",
    file_details_symlink: "Символическая ссылка",
    file_details_md5: "MD5",
    file_details_video_meta: "Метаданные видео",
    file_details_audio_meta: "Метаданные аудио",
    file_details_image_meta: "Метаданные изображения",
    choose_dir_first: "Сначала выберите каталог в дереве.",
    already_in_root: "Вы уже в корневом каталоге.",
    file_selected: "Выбран файл: {path}",
    file_path_copied: "Путь скопирован: {path}",
    file_activated: "Файл выбран: {path}",
    copy_path_failed: "Не удалось скопировать путь файла.",
    select_file_first: "Сначала выберите файл.",
    parent_nav_failed: "Не удалось перейти в родительский каталог.",
    file_action_failed: "Не удалось обработать выбранный файл.",
    no_files_in_dir: "Файлы в каталоге не найдены.",
    no_roots: "Нет добавленных путей сканирования.",
    no_search_results: "Ничего не найдено.",
    status_worker_alive: "доступен",
    status_worker_offline: "офлайн",
    status_stale_na: "n/a",
    status_line:
      "статус: {state} (ожидается: {desired}), режим: {mode}, worker: {worker} [stale={stale}], обработано: {processed}, сохранено: {emitted}, пропущено: {skipped}",
    scan_state_idle: "ожидание",
    scan_state_running: "в работе",
    scan_state_stopped: "остановлен",
    scan_state_failed: "ошибка",
    scan_mode_add_new_short: "добавление новых",
    scan_mode_rebuild_short: "пересоздание базы",
    err_load_tree_node: "Не удалось загрузить узел дерева: {message}",
    err_open_directory: "Не удалось открыть каталог: {message}",
    err_picker_failed: "Ошибка выбора каталога: {message}",
    err_start_failed: "Не удалось запустить сканирование: {message}",
    err_stop_failed: "Не удалось остановить сканирование: {message}",
    err_refresh_tree_failed: "Не удалось обновить дерево: {message}",
    err_search_failed: "Не удалось выполнить поиск: {message}",
    err_state_refresh_failed: "Не удалось обновить состояние: {message}",
    err_ui_init_failed: "Ошибка инициализации UI: {message}",
  },
  en: {
    app_title: "Catalogic STEP1",
    worker_warning: "Scanner worker offline. Start `catalogic-scanner` service.",
    tab_settings: "Settings",
    tab_tree: "Tree View",
    tab_state: "State",
    tab_duplicates: "Duplicate Search",
    settings_title: "Settings",
    settings_language_label: "UI language:",
    language_ru: "Russian",
    language_en: "English",
    root_input_placeholder: "/mnt/storage/media",
    open_picker_btn: "Choose folder",
    add_root_btn: "Add path",
    picker_up_btn: "Up",
    picker_select_btn: "Select current",
    picker_close_btn: "Close",
    scan_mode_label: "Scan mode:",
    scan_mode_add_new: "Add new",
    scan_mode_rebuild: "Rebuild database",
    follow_symlinks_label: "Follow symlink directories:",
    start_scan_btn: "Start scanner",
    stop_scan_btn: "Stop scanner",
    tree_title: "Tree View",
    tree_search_placeholder: "Name search (*, ?)",
    tree_search_btn: "Search",
    tree_refresh_btn: "Refresh tree",
    tree_dirs_title: "Directories",
    files_title: "Files",
    files_select_dir_left: "Select a directory on the left.",
    files_selection_default: "Select a file for actions.",
    file_details_title: "File Details",
    file_details_placeholder: "Select a file in the table to view full information.",
    state_title: "State",
    state_refresh_btn: "Refresh",
    state_scan: "Scanner",
    state_worker_process: "Worker process",
    state_metrics: "Metrics",
    state_utilities: "Utilities",
    dups_title: "Duplicate Search (name + size)",
    dups_refresh_btn: "Refresh",
    delete_root_btn: "Delete",
    pane_resize_title: "Resize panels",
    sort_name: "Name",
    sort_size: "Size",
    sort_mtime: "Modified",
    yes: "Yes",
    no: "No",
    na: "n/a",
    unknown: "unknown",
    loading_file_details: "Loading file details...",
    no_file_data: "No data for selected file.",
    file_details_error: "Failed to load file details.",
    file_details_path: "Path",
    file_details_name: "Name",
    file_details_size: "Size",
    file_details_mtime: "Modified",
    file_details_ctime: "Created",
    file_details_mime: "MIME",
    file_details_symlink: "Symbolic link",
    file_details_md5: "MD5",
    file_details_video_meta: "Video metadata",
    file_details_audio_meta: "Audio metadata",
    file_details_image_meta: "Image metadata",
    choose_dir_first: "Select a directory in the tree first.",
    already_in_root: "You are already at the root directory.",
    file_selected: "Selected file: {path}",
    file_path_copied: "Path copied: {path}",
    file_activated: "File selected: {path}",
    copy_path_failed: "Failed to copy file path.",
    select_file_first: "Select a file first.",
    parent_nav_failed: "Failed to navigate to parent directory.",
    file_action_failed: "Failed to process selected file.",
    no_files_in_dir: "No files found in this directory.",
    no_roots: "No scan paths configured.",
    no_search_results: "No results found.",
    status_worker_alive: "alive",
    status_worker_offline: "offline",
    status_stale_na: "n/a",
    status_line:
      "status: {state} (desired: {desired}), mode: {mode}, worker: {worker} [stale={stale}], processed: {processed}, emitted: {emitted}, skipped: {skipped}",
    scan_state_idle: "idle",
    scan_state_running: "running",
    scan_state_stopped: "stopped",
    scan_state_failed: "failed",
    scan_mode_add_new_short: "add new",
    scan_mode_rebuild_short: "rebuild",
    err_load_tree_node: "Load tree node failed: {message}",
    err_open_directory: "Open directory failed: {message}",
    err_picker_failed: "Directory picker failed: {message}",
    err_start_failed: "Start failed: {message}",
    err_stop_failed: "Stop failed: {message}",
    err_refresh_tree_failed: "Refresh tree failed: {message}",
    err_search_failed: "Search failed: {message}",
    err_state_refresh_failed: "State refresh failed: {message}",
    err_ui_init_failed: "UI init failed: {message}",
  },
};

let pickerCurrentPath = null;
const treeCache = new Map();
const fileDetailsCache = new Map();
let selectedDirKey = null;
let selectedDirContext = null;
let selectedFilePath = null;
let currentFiles = [];
const fileSort = { key: "name", direction: "asc" };
let currentLang = "ru";

function t(key, vars = {}) {
  const dict = I18N[currentLang] || I18N.ru;
  let text = dict[key] || I18N.ru[key] || key;
  Object.entries(vars).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, String(value));
  });
  return text;
}

function translateScanState(value) {
  const raw = String(value || "").toLowerCase();
  if (raw === "running") return t("scan_state_running");
  if (raw === "idle") return t("scan_state_idle");
  if (raw === "stopped") return t("scan_state_stopped");
  if (raw === "failed") return t("scan_state_failed");
  return value || t("unknown");
}

function translateScanMode(value) {
  const raw = String(value || "").toLowerCase();
  if (raw === "rebuild") return t("scan_mode_rebuild_short");
  return t("scan_mode_add_new_short");
}

function applyI18nToDocument() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (!key) return;
    node.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.dataset.i18nPlaceholder;
    if (!key) return;
    node.setAttribute("placeholder", t(key));
  });
  document.querySelectorAll("[data-i18n-title]").forEach((node) => {
    const key = node.dataset.i18nTitle;
    if (!key) return;
    node.setAttribute("title", t(key));
  });
  document.documentElement.setAttribute("lang", currentLang);
  document.title = t("app_title");
}

function normalizeLanguage(value) {
  if (typeof value !== "string") {
    return null;
  }
  const raw = value.trim().toLowerCase();
  if (raw.startsWith("en")) {
    return "en";
  }
  if (raw.startsWith("ru")) {
    return "ru";
  }
  return null;
}

function getLanguageFromQuery() {
  try {
    const value = new URLSearchParams(window.location.search).get("lang");
    return normalizeLanguage(value);
  } catch {
    return null;
  }
}

function detectBrowserLanguage() {
  const candidates = [];
  if (Array.isArray(navigator.languages)) {
    candidates.push(...navigator.languages);
  }
  candidates.push(navigator.language);
  for (const candidate of candidates) {
    const normalized = normalizeLanguage(candidate);
    if (normalized) {
      return normalized;
    }
  }
  return "ru";
}

function updateLangQueryParam(lang) {
  const normalized = normalizeLanguage(lang);
  if (!normalized) {
    return;
  }
  const url = new URL(window.location.href);
  if (url.searchParams.get("lang") === normalized) {
    return;
  }
  url.searchParams.set("lang", normalized);
  const next = `${url.pathname}?${url.searchParams.toString()}${url.hash}`;
  window.history.replaceState(null, "", next);
}

function initLanguage() {
  const queryLang = getLanguageFromQuery();
  if (queryLang) {
    currentLang = queryLang;
    window.localStorage.setItem(LANG_STORAGE_KEY, currentLang);
  } else {
    const saved = normalizeLanguage(window.localStorage.getItem(LANG_STORAGE_KEY));
    if (saved) {
      currentLang = saved;
    } else {
      currentLang = detectBrowserLanguage();
      window.localStorage.setItem(LANG_STORAGE_KEY, currentLang);
    }
  }
  const select = $("language-select");
  if (select) {
    select.value = currentLang;
  }
  applyI18nToDocument();
}

function setLanguage(lang) {
  currentLang = normalizeLanguage(lang) || "ru";
  window.localStorage.setItem(LANG_STORAGE_KEY, currentLang);
  updateLangQueryParam(currentLang);
  const select = $("language-select");
  if (select && select.value !== currentLang) {
    select.value = currentLang;
  }
  applyI18nToDocument();
  updateFilesTitle();
}

function updateFilesTitle() {
  const titleNode = $("files-title");
  if (!titleNode) {
    return;
  }
  if (!selectedDirContext) {
    titleNode.textContent = t("files_title");
    return;
  }
  titleNode.textContent = `${t("files_title")}: ${selectedDirContext.dirPath}`;
}

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
  const leftResizer = $("pane-resizer-left");
  const rightResizer = $("pane-resizer-right");
  if (!layout || !leftResizer || !rightResizer) {
    return;
  }

  const MIN_LEFT = 220;
  const MIN_MIDDLE = 320;
  const MIN_DETAILS = 280;
  const RESIZERS_WIDTH = 24;

  const readCurrentLeft = () => {
    const value = Number.parseFloat(getComputedStyle(layout).getPropertyValue("--left-pane-width"));
    return Number.isFinite(value) ? value : 420;
  };
  const readCurrentDetails = () => {
    const value = Number.parseFloat(getComputedStyle(layout).getPropertyValue("--details-pane-width"));
    return Number.isFinite(value) ? value : 400;
  };

  const applyLayoutWidths = (leftRaw, detailsRaw) => {
    const width = layout.clientWidth;
    if (width <= 0) {
      return null;
    }

    let left = Number.isFinite(leftRaw) ? Number(leftRaw) : readCurrentLeft();
    let details = Number.isFinite(detailsRaw) ? Number(detailsRaw) : readCurrentDetails();

    const maxLeft = Math.max(MIN_LEFT, width - MIN_MIDDLE - MIN_DETAILS - RESIZERS_WIDTH);
    left = Math.min(Math.max(left, MIN_LEFT), maxLeft);

    const maxDetails = Math.max(MIN_DETAILS, width - MIN_MIDDLE - left - RESIZERS_WIDTH);
    details = Math.min(Math.max(details, MIN_DETAILS), maxDetails);

    const maxLeftWithDetails = Math.max(MIN_LEFT, width - MIN_MIDDLE - details - RESIZERS_WIDTH);
    left = Math.min(Math.max(left, MIN_LEFT), maxLeftWithDetails);

    layout.style.setProperty("--left-pane-width", `${Math.round(left)}px`);
    layout.style.setProperty("--details-pane-width", `${Math.round(details)}px`);

    return { left, details };
  };

  const savedLeft = Number(window.localStorage.getItem(LEFT_PANEL_WIDTH_STORAGE_KEY));
  const savedDetails = Number(window.localStorage.getItem(DETAILS_PANEL_WIDTH_STORAGE_KEY));
  const appliedInit = applyLayoutWidths(savedLeft, savedDetails);
  if (appliedInit) {
    window.localStorage.setItem(LEFT_PANEL_WIDTH_STORAGE_KEY, String(appliedInit.left));
    window.localStorage.setItem(DETAILS_PANEL_WIDTH_STORAGE_KEY, String(appliedInit.details));
  }

  leftResizer.addEventListener("pointerdown", (event) => {
    if (window.matchMedia("(max-width: 900px)").matches) {
      return;
    }
    event.preventDefault();
    const rect = layout.getBoundingClientRect();
    layout.classList.add("resizing");
    leftResizer.setPointerCapture(event.pointerId);

    const updateWidth = (clientX) => {
      const nextWidth = clientX - rect.left;
      const applied = applyLayoutWidths(nextWidth, null);
      if (applied) {
        window.localStorage.setItem(LEFT_PANEL_WIDTH_STORAGE_KEY, String(applied.left));
        window.localStorage.setItem(DETAILS_PANEL_WIDTH_STORAGE_KEY, String(applied.details));
      }
    };

    const onMove = (moveEvent) => {
      updateWidth(moveEvent.clientX);
    };

    const onEnd = (endEvent) => {
      layout.classList.remove("resizing");
      if (leftResizer.hasPointerCapture(endEvent.pointerId)) {
        leftResizer.releasePointerCapture(endEvent.pointerId);
      }
      leftResizer.removeEventListener("pointermove", onMove);
      leftResizer.removeEventListener("pointerup", onEnd);
      leftResizer.removeEventListener("pointercancel", onEnd);
    };

    leftResizer.addEventListener("pointermove", onMove);
    leftResizer.addEventListener("pointerup", onEnd);
    leftResizer.addEventListener("pointercancel", onEnd);
  });

  rightResizer.addEventListener("pointerdown", (event) => {
    if (window.matchMedia("(max-width: 900px)").matches) {
      return;
    }
    event.preventDefault();
    const rect = layout.getBoundingClientRect();
    layout.classList.add("resizing");
    rightResizer.setPointerCapture(event.pointerId);

    const updateWidth = (clientX) => {
      const nextWidth = rect.right - clientX;
      const applied = applyLayoutWidths(null, nextWidth);
      if (applied) {
        window.localStorage.setItem(LEFT_PANEL_WIDTH_STORAGE_KEY, String(applied.left));
        window.localStorage.setItem(DETAILS_PANEL_WIDTH_STORAGE_KEY, String(applied.details));
      }
    };

    const onMove = (moveEvent) => {
      updateWidth(moveEvent.clientX);
    };

    const onEnd = (endEvent) => {
      layout.classList.remove("resizing");
      if (rightResizer.hasPointerCapture(endEvent.pointerId)) {
        rightResizer.releasePointerCapture(endEvent.pointerId);
      }
      rightResizer.removeEventListener("pointermove", onMove);
      rightResizer.removeEventListener("pointerup", onEnd);
      rightResizer.removeEventListener("pointercancel", onEnd);
    };

    rightResizer.addEventListener("pointermove", onMove);
    rightResizer.addEventListener("pointerup", onEnd);
    rightResizer.addEventListener("pointercancel", onEnd);
  });

  window.addEventListener("resize", () => {
    const currentLeft = readCurrentLeft();
    const currentDetails = readCurrentDetails();
    const applied = applyLayoutWidths(currentLeft, currentDetails);
    if (applied) {
      window.localStorage.setItem(LEFT_PANEL_WIDTH_STORAGE_KEY, String(applied.left));
      window.localStorage.setItem(DETAILS_PANEL_WIDTH_STORAGE_KEY, String(applied.details));
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
  return date.toLocaleString(currentLang);
}

function toPrettyJson(value) {
  return JSON.stringify(value, null, 2);
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
    return String(a.name || "").localeCompare(String(b.name || ""), currentLang, {
      sensitivity: "base",
    }) * dir;
  });
  return sorted;
}

function updateSortButtons() {
  const labels = {
    name: t("sort_name"),
    size: t("sort_size"),
    mtime: t("sort_mtime"),
  };
  const arrow = fileSort.direction === "asc" ? "↑" : "↓";
  $("sort-name-btn").textContent = `${labels.name}${fileSort.key === "name" ? ` ${arrow}` : ""}`;
  $("sort-size-btn").textContent = `${labels.size}${fileSort.key === "size" ? ` ${arrow}` : ""}`;
  $("sort-mtime-btn").textContent = `${labels.mtime}${fileSort.key === "mtime" ? ` ${arrow}` : ""}`;
}

function toMetaText(meta) {
  if (!meta || typeof meta !== "object") {
    return t("na");
  }
  return JSON.stringify(meta, null, 2);
}

function renderFileDetails(details) {
  const panel = $("file-details-panel");
  if (!panel) {
    return;
  }
  if (!details) {
    panel.textContent = t("no_file_data");
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

  addPair(t("file_details_path"), details.path || "-");
  addPair(t("file_details_name"), details.name || "-");
  addPair(t("file_details_size"), `${formatSize(details.size)} (${Number(details.size || 0)} B)`);
  addPair(t("file_details_mtime"), formatDateTime(details.mtime));
  addPair(t("file_details_ctime"), formatDateTime(details.ctime));
  addPair(t("file_details_mime"), details.mime || "-");
  addPair(t("file_details_symlink"), details.is_symlink ? t("yes") : t("no"));
  addPair(t("file_details_md5"), details.md5 || t("na"));

  const sections = [
    { title: t("file_details_video_meta"), payload: details.video_meta },
    { title: t("file_details_audio_meta"), payload: details.audio_meta },
    { title: t("file_details_image_meta"), payload: details.image_meta },
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
  setFileDetailsPlaceholder(t("loading_file_details"));
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
  setFilesSelectionInfo(t("file_selected", { path: item.path }));
  renderFilesTable();
  if (selectedDirContext) {
    loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
      setFileDetailsPlaceholder(t("file_details_error"));
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
    setFilesSelectionInfo(t("choose_dir_first"));
    return;
  }
  const currentPath = normalizePath(selectedDirContext.dirPath);
  const rootPath = normalizePath(selectedDirContext.rootPath);
  if (currentPath === rootPath) {
    setFilesSelectionInfo(t("already_in_root"));
    return;
  }

  const parentPath = normalizePath(getParentPath(currentPath));
  const targetPath = isInsideRoot(parentPath, rootPath) ? parentPath : rootPath;
  await selectDirectory(selectedDirContext.rootId, targetPath);
  setFilesSelectionInfo(`${t("tree_dirs_title")}: ${targetPath}`);
}

async function activateFile(item) {
  if (!item) {
    return;
  }
  selectedFilePath = item.path;
  renderFilesTable();
  const copied = await tryCopyToClipboard(item.path);
  if (copied) {
    setFilesSelectionInfo(t("file_path_copied", { path: item.path }));
  } else {
    setFilesSelectionInfo(t("file_activated", { path: item.path }));
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
    td.textContent = t("no_files_in_dir");
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
      setFilesSelectionInfo(t("file_selected", { path: item.path }));
      renderFilesTable();
      if (selectedDirContext) {
        loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
          setFileDetailsPlaceholder(t("file_details_error"));
        });
      }
    };
    tr.ondblclick = () => {
      activateFile(item).catch(() => {
        setFilesSelectionInfo(t("file_activated", { path: item.path }));
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

async function selectDirectory(rootId, dirPath) {
  const data = await getDirData(rootId, dirPath);
  selectedDirContext = {
    rootId: Number(rootId),
    rootPath: normalizePath(data.rootPath || dirPath),
    dirPath: normalizePath(data.dirPath || dirPath),
  };
  selectedDirKey = treeKey(rootId, selectedDirContext.dirPath);
  selectedFilePath = null;
  currentFiles = data.files || [];
  updateFilesTitle();
  setFilesSelectionInfo(t("files_selection_default"));
  setFileDetailsPlaceholder(t("file_details_placeholder"));
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
    expand().catch((err) => alert(t("err_load_tree_node", { message: err.message })));
  };

  name.onclick = () => {
    selectDirectory(rootId, item.path).catch((err) => {
      alert(t("err_open_directory", { message: err.message }));
    });
  };

  name.ondblclick = () => {
    selectDirectory(rootId, item.path).catch((err) => {
      alert(t("err_open_directory", { message: err.message }));
    });
    if (toggle.textContent !== "·") {
      expand().catch((err) => alert(t("err_load_tree_node", { message: err.message })));
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
        expand().catch((err) => alert(t("err_load_tree_node", { message: err.message })));
      }
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      event.stopPropagation();
      if (expanded && toggle.textContent !== "·") {
        expand().catch((err) => alert(t("err_load_tree_node", { message: err.message })));
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
  updateFilesTitle();
  setFilesSelectionInfo(t("files_selection_default"));
  setFileDetailsPlaceholder(t("file_details_placeholder"));
  renderFilesTable();

  const container = $("tree-result");
  container.innerHTML = "";
  if (!roots.length) {
    container.textContent = t("no_roots");
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
    box.textContent = t("no_search_results");
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
    del.textContent = t("delete_root_btn");
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
  const worker = status.worker_alive ? t("status_worker_alive") : t("status_worker_offline");
  const stale =
    status.worker_stale_sec === null || status.worker_stale_sec === undefined
      ? t("status_stale_na")
      : `${Number(status.worker_stale_sec).toFixed(1)}s`;
  const mode = translateScanMode(status.scan_mode);
  $("scan-status").textContent =
    t("status_line", {
      state: translateScanState(status.state),
      desired: translateScanState(status.desired_state),
      mode,
      worker,
      stale,
      processed: status.processed_files,
      emitted: status.emitted_records,
      skipped: status.skipped_files,
    });

  const scanMode = $("scan-mode-select");
  const scanActive = status.state === "running" || status.desired_state === "running";
  if (scanMode) {
    if (scanActive && status.scan_mode) {
      scanMode.value = status.scan_mode;
    }
    scanMode.disabled = scanActive;
  }
  const followInput = $("follow-symlinks-input");
  if (followInput) {
    if (scanActive) {
      followInput.checked = Boolean(status.follow_symlinks);
    }
    followInput.disabled = scanActive;
  }

  const startBtn = $("start-scan-btn");
  const stopBtn = $("stop-scan-btn");
  const warning = $("worker-warning");
  const workerAlive = Boolean(status.worker_alive);

  startBtn.disabled = !workerAlive;
  stopBtn.disabled = status.state !== "running" && status.desired_state !== "running";
  warning.classList.toggle("hidden", workerAlive);
}

async function refreshState() {
  const data = await api("/api/state");
  $("state-scan").textContent = toPrettyJson(data.scan || {});
  $("state-process").textContent = toPrettyJson(data.process || {});
  $("state-metrics").textContent = toPrettyJson(data.metrics || {});
  $("state-utils").textContent = toPrettyJson(data.utilities || {});
}

function bindActions() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.onclick = () => {
      switchTab(tab.dataset.tab);
      if (tab.dataset.tab === "state") {
        refreshState().catch(() => {});
      }
    };
  });

  $("sort-name-btn").onclick = () => setFileSort("name");
  $("sort-size-btn").onclick = () => setFileSort("size");
  $("sort-mtime-btn").onclick = () => setFileSort("mtime");
  $("language-select").onchange = async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLSelectElement)) {
      return;
    }
    setLanguage(target.value);
    updateSortButtons();
    renderFilesTable();
    if (selectedDirContext && selectedFilePath) {
      const key = `${String(selectedDirContext.rootId)}:${selectedFilePath}`;
      const cached = fileDetailsCache.get(key);
      if (cached) {
        renderFileDetails(cached);
      } else {
        await loadAndRenderFileDetails(selectedDirContext.rootId, selectedFilePath).catch(() => {
          setFileDetailsPlaceholder(t("file_details_error"));
        });
      }
      setFilesSelectionInfo(t("file_selected", { path: selectedFilePath }));
    } else {
      setFileDetailsPlaceholder(t("file_details_placeholder"));
      if (!selectedFilePath) {
        setFilesSelectionInfo(t("files_selection_default"));
      }
    }
    await refreshRoots().catch(() => {});
    await refreshStatus().catch(() => {});
    await refreshState().catch(() => {});
  };

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
      alert(t("err_picker_failed", { message: err.message }));
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
      const scanMode = $("scan-mode-select").value;
      const followSymlinks = Boolean($("follow-symlinks-input").checked);
      await api("/api/scan/start", {
        method: "POST",
        body: JSON.stringify({
          scan_mode: scanMode,
          follow_symlinks: followSymlinks,
        }),
      });
    } catch (err) {
      alert(t("err_start_failed", { message: err.message }));
    }
    await refreshStatus();
    await refreshState().catch(() => {});
  };

  $("stop-scan-btn").onclick = async () => {
    try {
      await api("/api/scan/stop", { method: "POST" });
    } catch (err) {
      alert(t("err_stop_failed", { message: err.message }));
    }
    await refreshStatus();
    await refreshState().catch(() => {});
  };

  $("tree-refresh-btn").onclick = async () => {
    try {
      await refreshTree();
    } catch (err) {
      alert(t("err_refresh_tree_failed", { message: err.message }));
    }
  };

  $("tree-search-btn").onclick = async () => {
    try {
      await runTreeSearch();
    } catch (err) {
      alert(t("err_search_failed", { message: err.message }));
    }
  };

  $("dups-refresh-btn").onclick = refreshDuplicates;
  $("state-refresh-btn").onclick = async () => {
    try {
      await refreshState();
    } catch (err) {
      alert(t("err_state_refresh_failed", { message: err.message }));
    }
  };

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
        setFilesSelectionInfo(t("select_file_first"));
        return;
      }
      activateSelectedFile().catch(() => {
        setFilesSelectionInfo(t("copy_path_failed"));
      });
      return;
    }

    if (event.key === "Backspace") {
      event.preventDefault();
      navigateToParentDirectory().catch(() => {
        setFilesSelectionInfo(t("parent_nav_failed"));
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
        setFilesSelectionInfo(t("file_action_failed"));
      });
    }
  });
}

async function bootstrap() {
  initLanguage();
  initBrowserPaneResize();
  bindActions();
  updateSortButtons();
  await refreshRoots();
  await refreshStatus();
  await refreshState();
  await refreshTree();
  await refreshDuplicates();
  setInterval(() => {
    refreshStatus().catch(() => {});
    const stateTab = $("tab-state");
    if (stateTab && stateTab.classList.contains("active")) {
      refreshState().catch(() => {});
    }
  }, 2000);
}

bootstrap().catch((err) => {
  console.error(err);
  alert(t("err_ui_init_failed", { message: err.message }));
});
