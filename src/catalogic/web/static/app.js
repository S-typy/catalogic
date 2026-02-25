const $ = (id) => document.getElementById(id);
const API_BASE = window.CATALOGIC_API_BASE || "";
const LEFT_PANEL_WIDTH_STORAGE_KEY = "catalogic_tree_left_panel_width";
const DETAILS_PANEL_WIDTH_STORAGE_KEY = "catalogic_tree_details_panel_width";
const LANG_STORAGE_KEY = "catalogic_ui_language";
const PREVIEW_AUTOSTART_STORAGE_KEY = "catalogic_preview_autostart";
const VIDEO_VIEWER_PAN_START_DISTANCE = 5;
const VIDEO_VIEWER_CONTROLS_ZONE_MIN_HEIGHT = 44;
const VIDEO_VIEWER_CONTROLS_ZONE_MAX_HEIGHT = 78;
const VIDEO_VIEWER_CONTROLS_ZONE_HEIGHT_RATIO = 0.07;
const VIDEO_VIEWER_CONTROLS_ZONE_EXTRA_TOP = 6;

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
    root_add_path_label: "Путь для добавления:",
    root_input_placeholder: "/mnt/storage/media",
    open_picker_btn: "Выбрать каталог",
    add_root_btn: "Добавить путь",
    scan_paths_title: "Пути сканирования",
    picker_up_btn: "Вверх",
    picker_select_btn: "Выбрать текущий",
    picker_close_btn: "Закрыть",
    scan_mode_label: "Режим сканирования:",
    scan_mode_add_new: "Добавление новых",
    scan_mode_rebuild: "Пересоздание базы",
    follow_symlinks_label: "Следовать symlink-директориям:",
    preview_autostart_label: "Автостарт превью видео:",
    scanner_controls_label: "Управление сканером:",
    start_scan_btn: "Старт сканера",
    stop_scan_btn: "Стоп сканера",
    perf_settings_title: "Производительность сканера",
    hash_mode_label: "Режим хэша:",
    hash_mode_auto: "Авто",
    hash_mode_full: "Полный MD5",
    hash_mode_sample: "Сэмплированный",
    hash_threshold_label: "Порог sample (MB):",
    hash_chunk_label: "Размер sample блока (MB):",
    ffprobe_timeout_label: "ffprobe timeout (sec):",
    ffprobe_analyze_label: "ffprobe analyzeduration (us):",
    ffprobe_probesize_label: "ffprobe probesize (bytes):",
    save_settings_btn: "Сохранить настройки",
    reset_settings_btn: "Сбросить по умолчанию",
    runtime_settings_saved: "Настройки сканера сохранены.",
    runtime_settings_reset: "Настройки сканера сброшены к значениям по умолчанию.",
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
    file_preview_loading: "Загрузка превью...",
    file_preview_not_available: "Превью недоступно для этого типа файла.",
    file_preview_failed: "Не удалось загрузить превью файла.",
    file_preview_video_seek_hint: "Перемотка перезапускает поток с выбранного момента.",
    viewer_btn_100: "100%",
    viewer_btn_fit: "По экрану",
    viewer_btn_fragment: "Фрагмент",
    viewer_btn_close: "Закрыть",
    viewer_fragment_mode_on: "Режим выделения: включен",
    viewer_fragment_mode_off: "Режим выделения: выключен",
    viewer_status_scale: "Масштаб: {percent}%",
    viewer_status_scale_fragment: "Масштаб: {percent}% | выделение",
    viewer_open_failed: "Не удалось открыть просмотрщик: {message}",
    video_viewer_btn_close: "Закрыть",
    video_viewer_status_loading: "Открытие видео...",
    video_viewer_status_ready: "Готово к воспроизведению",
    video_viewer_status_fallback: "Исходный формат не поддержан браузером, включен поток preview",
    video_viewer_status_error: "Не удалось загрузить видео",
    file_details_video_meta: "Метаданные видео",
    file_details_audio_meta: "Метаданные аудио",
    file_details_image_meta: "Метаданные изображения",
    parent_dir_name: "..",
    dir_selected: "Выбран каталог: {path}",
    up_dir_selected: "Переход на уровень выше: {path}",
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
    status_current_file: "текущий файл: {path}",
    status_current_file_none: "текущий файл: нет",
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
    err_settings_load_failed: "Не удалось загрузить настройки: {message}",
    err_settings_save_failed: "Не удалось сохранить настройки: {message}",
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
    root_add_path_label: "Path to add:",
    root_input_placeholder: "/mnt/storage/media",
    open_picker_btn: "Choose folder",
    add_root_btn: "Add path",
    scan_paths_title: "Scan paths",
    picker_up_btn: "Up",
    picker_select_btn: "Select current",
    picker_close_btn: "Close",
    scan_mode_label: "Scan mode:",
    scan_mode_add_new: "Add new",
    scan_mode_rebuild: "Rebuild database",
    follow_symlinks_label: "Follow symlink directories:",
    preview_autostart_label: "Autostart video preview:",
    scanner_controls_label: "Scanner controls:",
    start_scan_btn: "Start scanner",
    stop_scan_btn: "Stop scanner",
    perf_settings_title: "Scanner Performance",
    hash_mode_label: "Hash mode:",
    hash_mode_auto: "Auto",
    hash_mode_full: "Full MD5",
    hash_mode_sample: "Sampled",
    hash_threshold_label: "Sample threshold (MB):",
    hash_chunk_label: "Sample chunk size (MB):",
    ffprobe_timeout_label: "ffprobe timeout (sec):",
    ffprobe_analyze_label: "ffprobe analyzeduration (us):",
    ffprobe_probesize_label: "ffprobe probesize (bytes):",
    save_settings_btn: "Save settings",
    reset_settings_btn: "Reset defaults",
    runtime_settings_saved: "Scanner settings saved.",
    runtime_settings_reset: "Scanner settings reset to defaults.",
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
    file_preview_loading: "Loading preview...",
    file_preview_not_available: "Preview is not available for this file type.",
    file_preview_failed: "Failed to load file preview.",
    file_preview_video_seek_hint: "Seeking reloads the stream from selected position.",
    viewer_btn_100: "100%",
    viewer_btn_fit: "Fit",
    viewer_btn_fragment: "Fragment",
    viewer_btn_close: "Close",
    viewer_fragment_mode_on: "Selection mode: enabled",
    viewer_fragment_mode_off: "Selection mode: disabled",
    viewer_status_scale: "Zoom: {percent}%",
    viewer_status_scale_fragment: "Zoom: {percent}% | selection",
    viewer_open_failed: "Failed to open viewer: {message}",
    video_viewer_btn_close: "Close",
    video_viewer_status_loading: "Opening video...",
    video_viewer_status_ready: "Ready to play",
    video_viewer_status_fallback: "Source format is not supported by browser, preview stream enabled",
    video_viewer_status_error: "Failed to load video",
    file_details_video_meta: "Video metadata",
    file_details_audio_meta: "Audio metadata",
    file_details_image_meta: "Image metadata",
    parent_dir_name: "..",
    dir_selected: "Selected directory: {path}",
    up_dir_selected: "Navigate up: {path}",
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
    status_current_file: "current file: {path}",
    status_current_file_none: "current file: none",
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
    err_settings_load_failed: "Failed to load settings: {message}",
    err_settings_save_failed: "Failed to save settings: {message}",
  },
};

let pickerCurrentPath = null;
const treeCache = new Map();
const fileDetailsCache = new Map();
let selectedDirKey = null;
let selectedDirContext = null;
let selectedRowPath = null;
let selectedRowType = null;
let currentFiles = [];
const fileSort = { key: "name", direction: "asc" };
let currentLang = "ru";
let previewAutostart = false;
const imageViewerState = {
  open: false,
  rootId: null,
  path: null,
  naturalWidth: 0,
  naturalHeight: 0,
  scale: 1,
  offsetX: 0,
  offsetY: 0,
  fragmentMode: false,
  pendingPan: false,
  dragging: false,
  dragStartX: 0,
  dragStartY: 0,
  dragOriginOffsetX: 0,
  dragOriginOffsetY: 0,
  selecting: false,
  selectStartX: 0,
  selectStartY: 0,
};
const videoViewerState = {
  open: false,
  rootId: null,
  path: null,
  naturalWidth: 0,
  naturalHeight: 0,
  scale: 1,
  offsetX: 0,
  offsetY: 0,
  fragmentMode: false,
  dragging: false,
  dragStartX: 0,
  dragStartY: 0,
  dragOriginOffsetX: 0,
  dragOriginOffsetY: 0,
  selecting: false,
  selectStartX: 0,
  selectStartY: 0,
  statusNote: "",
  hasInitialLayout: false,
  fallbackUsed: false,
  fallbackReloading: false,
  fallbackSkipNextSeeking: false,
};

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
  if (imageViewerState.open) {
    updateImageViewerStatus();
  }
  if (videoViewerState.open) {
    updateVideoViewerStatus();
  }
}

function readPreviewAutostartSetting() {
  const raw = String(window.localStorage.getItem(PREVIEW_AUTOSTART_STORAGE_KEY) || "").toLowerCase();
  return raw === "1" || raw === "true" || raw === "yes" || raw === "on";
}

function applyPreviewAutostartSetting(value, { persist = true, rerender = true } = {}) {
  previewAutostart = Boolean(value);
  if (persist) {
    window.localStorage.setItem(PREVIEW_AUTOSTART_STORAGE_KEY, previewAutostart ? "1" : "0");
  }
  const checkbox = $("preview-autostart-input");
  if (checkbox) {
    checkbox.checked = previewAutostart;
  }
  if (!rerender || !selectedDirContext || !selectedRowPath || selectedRowType !== "file") {
    return;
  }
  const key = `${String(selectedDirContext.rootId)}:${selectedRowPath}`;
  const cached = fileDetailsCache.get(key);
  if (cached) {
    renderFileDetails(cached);
    return;
  }
  loadAndRenderFileDetails(selectedDirContext.rootId, selectedRowPath).catch(() => {
    setFileDetailsPlaceholder(t("file_details_error"));
  });
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

function setRuntimeSettingsStatus(text, isError = false) {
  const node = $("runtime-settings-status");
  if (!node) {
    return;
  }
  node.textContent = text || "";
  node.style.color = isError ? "#b42318" : "";
}

function setRuntimeSettingsControlsDisabled(disabled) {
  const ids = [
    "hash-mode-select",
    "hash-threshold-input",
    "hash-chunk-input",
    "ffprobe-timeout-input",
    "ffprobe-analyze-input",
    "ffprobe-probesize-input",
    "save-runtime-settings-btn",
    "reset-runtime-settings-btn",
  ];
  ids.forEach((id) => {
    const node = $(id);
    if (node) {
      node.disabled = Boolean(disabled);
    }
  });
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

function buildApiUrl(path, query = {}) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") {
      return;
    }
    params.set(key, String(value));
  });
  const qs = params.toString();
  return `${API_BASE}${path}${qs ? `?${qs}` : ""}`;
}

function extractApiErrorMessage(raw) {
  const text = String(raw || "").trim();
  if (!text) {
    return "";
  }
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object") {
      if (typeof parsed.detail === "string" && parsed.detail.trim()) {
        return parsed.detail.trim();
      }
      if (Array.isArray(parsed.detail) && parsed.detail.length) {
        const first = parsed.detail[0];
        if (typeof first === "string") {
          return first;
        }
        if (first && typeof first === "object" && typeof first.msg === "string") {
          return first.msg;
        }
      }
    }
  } catch (_) {
    // keep raw text fallback
  }
  return text;
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
  const rank = (item) => {
    if (isUpRow(item)) return 0;
    if (isDirRow(item)) return 1;
    return 2;
  };
  sorted.sort((a, b) => {
    const rankDiff = rank(a) - rank(b);
    if (rankDiff !== 0) {
      return rankDiff;
    }
    if (isUpRow(a) && isUpRow(b)) {
      return 0;
    }
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

function isUpRow(item) {
  return item && item.type === "up";
}

function isDirRow(item) {
  return item && item.type === "dir";
}

function isFileRow(item) {
  return item && item.type === "file";
}

function getSelectedRow() {
  if (!selectedRowPath || !selectedRowType) {
    return null;
  }
  return (
    currentFiles.find((item) => item.path === selectedRowPath && item.type === selectedRowType) || null
  );
}

function setSelectionFromRow(item) {
  if (!item) {
    selectedRowPath = null;
    selectedRowType = null;
    return;
  }
  selectedRowPath = item.path;
  selectedRowType = item.type;
}

function selectionInfoForRow(item) {
  if (isFileRow(item)) {
    return t("file_selected", { path: item.path });
  }
  if (isUpRow(item)) {
    return t("up_dir_selected", { path: item.path });
  }
  if (isDirRow(item)) {
    return t("dir_selected", { path: item.path });
  }
  return t("files_selection_default");
}

function isImageMime(mime) {
  return String(mime || "").toLowerCase().startsWith("image/");
}

function isVideoMime(mime) {
  return String(mime || "").toLowerCase().startsWith("video/");
}

function isImageName(name) {
  return /\.(jpg|jpeg|png|webp|gif|bmp|tif|tiff|avif|heic|heif)$/i.test(String(name || ""));
}

function isVideoName(name) {
  return /\.(mp4|mkv|avi|mov|webm|m4v|ts|m2ts|mpeg|mpg|wmv|flv)$/i.test(String(name || ""));
}

function updateImageViewerStatus() {
  const status = $("viewer-status");
  const fragmentBtn = $("viewer-fragment-btn");
  const canvas = $("image-viewer-canvas");
  if (!status || !fragmentBtn || !canvas) {
    return;
  }
  const percent = Math.round((Number(imageViewerState.scale) || 1) * 100);
  status.textContent = imageViewerState.fragmentMode
    ? t("viewer_status_scale_fragment", { percent })
    : t("viewer_status_scale", { percent });
  fragmentBtn.classList.toggle("active", imageViewerState.fragmentMode);
  canvas.classList.toggle("fragment-mode", imageViewerState.fragmentMode);
  canvas.classList.toggle("panning", imageViewerState.dragging);
}

function renderImageViewerTransform() {
  const img = $("image-viewer-img");
  if (!img) {
    return;
  }
  img.style.transform = `translate(${imageViewerState.offsetX}px, ${imageViewerState.offsetY}px) scale(${imageViewerState.scale})`;
  updateImageViewerStatus();
}

function getImageViewerCanvasSize() {
  const canvas = $("image-viewer-canvas");
  if (!canvas) {
    return { width: 0, height: 0 };
  }
  return { width: canvas.clientWidth, height: canvas.clientHeight };
}

function getImageViewerFitScale() {
  const { naturalWidth, naturalHeight } = imageViewerState;
  const { width, height } = getImageViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return 1;
  }
  return Math.min(width / naturalWidth, height / naturalHeight);
}

function applyImageViewerScale(newScale, anchorX = null, anchorY = null) {
  const { width, height } = getImageViewerCanvasSize();
  if (!width || !height) {
    return;
  }
  const minScale = Math.min(0.02, getImageViewerFitScale());
  const maxScale = 20;
  const nextScale = Math.min(Math.max(newScale, minScale), maxScale);
  const oldScale = imageViewerState.scale || 1;
  const ax = anchorX ?? width / 2;
  const ay = anchorY ?? height / 2;
  imageViewerState.offsetX = ax - ((ax - imageViewerState.offsetX) * nextScale) / oldScale;
  imageViewerState.offsetY = ay - ((ay - imageViewerState.offsetY) * nextScale) / oldScale;
  imageViewerState.scale = nextScale;
  renderImageViewerTransform();
}

function fitImageViewerToScreen() {
  const { naturalWidth, naturalHeight } = imageViewerState;
  const { width, height } = getImageViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return;
  }
  imageViewerState.scale = getImageViewerFitScale();
  imageViewerState.offsetX = (width - naturalWidth * imageViewerState.scale) / 2;
  imageViewerState.offsetY = (height - naturalHeight * imageViewerState.scale) / 2;
  renderImageViewerTransform();
}

function setImageViewerScale100() {
  const { naturalWidth, naturalHeight } = imageViewerState;
  const { width, height } = getImageViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return;
  }
  imageViewerState.scale = 1;
  imageViewerState.offsetX = (width - naturalWidth) / 2;
  imageViewerState.offsetY = (height - naturalHeight) / 2;
  renderImageViewerTransform();
}

function setImageViewerFragmentMode(enabled) {
  imageViewerState.fragmentMode = Boolean(enabled);
  updateImageViewerStatus();
}

function hideImageViewerSelection() {
  imageViewerState.selecting = false;
  const selection = $("image-viewer-selection");
  if (selection) {
    selection.classList.add("hidden");
  }
}

function zoomImageViewerToSelection(left, top, width, height) {
  const { naturalWidth, naturalHeight, scale, offsetX, offsetY } = imageViewerState;
  const { width: canvasWidth, height: canvasHeight } = getImageViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !scale || !canvasWidth || !canvasHeight) {
    return;
  }
  const x1 = Math.max(0, Math.min(naturalWidth, (left - offsetX) / scale));
  const y1 = Math.max(0, Math.min(naturalHeight, (top - offsetY) / scale));
  const x2 = Math.max(0, Math.min(naturalWidth, (left + width - offsetX) / scale));
  const y2 = Math.max(0, Math.min(naturalHeight, (top + height - offsetY) / scale));
  const selectedW = x2 - x1;
  const selectedH = y2 - y1;
  if (selectedW < 2 || selectedH < 2) {
    return;
  }

  const nextScale = Math.min(canvasWidth / selectedW, canvasHeight / selectedH);
  imageViewerState.scale = nextScale;
  imageViewerState.offsetX = -x1 * nextScale + (canvasWidth - selectedW * nextScale) / 2;
  imageViewerState.offsetY = -y1 * nextScale + (canvasHeight - selectedH * nextScale) / 2;
  renderImageViewerTransform();
}

function updateVideoViewerStatus() {
  const status = $("video-viewer-status");
  const fragmentBtn = $("video-viewer-fragment-btn");
  const canvas = $("video-viewer-canvas");
  if (!status || !fragmentBtn || !canvas) {
    return;
  }
  const percent = Math.round((Number(videoViewerState.scale) || 1) * 100);
  const zoomText = videoViewerState.fragmentMode
    ? t("viewer_status_scale_fragment", { percent })
    : t("viewer_status_scale", { percent });
  status.textContent = videoViewerState.statusNote
    ? `${videoViewerState.statusNote} | ${zoomText}`
    : zoomText;
  fragmentBtn.classList.toggle("active", videoViewerState.fragmentMode);
  canvas.classList.toggle("fragment-mode", videoViewerState.fragmentMode);
  canvas.classList.toggle("panning", videoViewerState.dragging);
}

function renderVideoViewerTransform() {
  const player = $("video-viewer-player");
  if (!player) {
    return;
  }
  player.style.transform = `translate(${videoViewerState.offsetX}px, ${videoViewerState.offsetY}px) scale(${videoViewerState.scale})`;
  updateVideoViewerStatus();
}

function getVideoViewerCanvasSize() {
  const canvas = $("video-viewer-canvas");
  if (!canvas) {
    return { width: 0, height: 0 };
  }
  return { width: canvas.clientWidth, height: canvas.clientHeight };
}

function getVideoViewerDisplayRect() {
  const { naturalWidth, naturalHeight, scale, offsetX, offsetY } = videoViewerState;
  if (!naturalWidth || !naturalHeight || !scale) {
    return null;
  }
  return {
    x: offsetX,
    y: offsetY,
    width: naturalWidth * scale,
    height: naturalHeight * scale,
  };
}

function isPointInVideoViewerControlZone(point) {
  const rect = getVideoViewerDisplayRect();
  if (!rect) {
    return false;
  }
  const insideX = point.x >= rect.x && point.x <= rect.x + rect.width;
  const insideY = point.y >= rect.y && point.y <= rect.y + rect.height;
  if (!insideX || !insideY) {
    return false;
  }
  const controlsBandHeight = Math.min(
    VIDEO_VIEWER_CONTROLS_ZONE_MAX_HEIGHT,
    Math.max(VIDEO_VIEWER_CONTROLS_ZONE_MIN_HEIGHT, rect.height * VIDEO_VIEWER_CONTROLS_ZONE_HEIGHT_RATIO)
  );
  const zoneTop = rect.y + rect.height - controlsBandHeight - VIDEO_VIEWER_CONTROLS_ZONE_EXTRA_TOP;
  return point.y >= zoneTop;
}

function getVideoViewerFitScale() {
  const { naturalWidth, naturalHeight } = videoViewerState;
  const { width, height } = getVideoViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return 1;
  }
  return Math.min(width / naturalWidth, height / naturalHeight);
}

function applyVideoViewerScale(newScale, anchorX = null, anchorY = null) {
  const { width, height } = getVideoViewerCanvasSize();
  if (!width || !height) {
    return;
  }
  const minScale = Math.min(0.05, getVideoViewerFitScale());
  const maxScale = 20;
  const nextScale = Math.min(Math.max(newScale, minScale), maxScale);
  const oldScale = videoViewerState.scale || 1;
  const ax = anchorX ?? width / 2;
  const ay = anchorY ?? height / 2;
  videoViewerState.offsetX = ax - ((ax - videoViewerState.offsetX) * nextScale) / oldScale;
  videoViewerState.offsetY = ay - ((ay - videoViewerState.offsetY) * nextScale) / oldScale;
  videoViewerState.scale = nextScale;
  renderVideoViewerTransform();
}

function fitVideoViewerToScreen() {
  const { naturalWidth, naturalHeight } = videoViewerState;
  const { width, height } = getVideoViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return;
  }
  videoViewerState.scale = getVideoViewerFitScale();
  videoViewerState.offsetX = (width - naturalWidth * videoViewerState.scale) / 2;
  videoViewerState.offsetY = (height - naturalHeight * videoViewerState.scale) / 2;
  renderVideoViewerTransform();
}

function setVideoViewerScale100() {
  const { naturalWidth, naturalHeight } = videoViewerState;
  const { width, height } = getVideoViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !width || !height) {
    return;
  }
  videoViewerState.scale = 1;
  videoViewerState.offsetX = (width - naturalWidth) / 2;
  videoViewerState.offsetY = (height - naturalHeight) / 2;
  renderVideoViewerTransform();
}

function setVideoViewerFragmentMode(enabled) {
  videoViewerState.fragmentMode = Boolean(enabled);
  updateVideoViewerStatus();
}

function hideVideoViewerSelection() {
  videoViewerState.selecting = false;
  const selection = $("video-viewer-selection");
  if (selection) {
    selection.classList.add("hidden");
  }
}

function zoomVideoViewerToSelection(left, top, width, height) {
  const { naturalWidth, naturalHeight, scale, offsetX, offsetY } = videoViewerState;
  const { width: canvasWidth, height: canvasHeight } = getVideoViewerCanvasSize();
  if (!naturalWidth || !naturalHeight || !scale || !canvasWidth || !canvasHeight) {
    return;
  }
  const x1 = Math.max(0, Math.min(naturalWidth, (left - offsetX) / scale));
  const y1 = Math.max(0, Math.min(naturalHeight, (top - offsetY) / scale));
  const x2 = Math.max(0, Math.min(naturalWidth, (left + width - offsetX) / scale));
  const y2 = Math.max(0, Math.min(naturalHeight, (top + height - offsetY) / scale));
  const selectedW = x2 - x1;
  const selectedH = y2 - y1;
  if (selectedW < 2 || selectedH < 2) {
    return;
  }
  const nextScale = Math.min(canvasWidth / selectedW, canvasHeight / selectedH);
  videoViewerState.scale = nextScale;
  videoViewerState.offsetX = -x1 * nextScale + (canvasWidth - selectedW * nextScale) / 2;
  videoViewerState.offsetY = -y1 * nextScale + (canvasHeight - selectedH * nextScale) / 2;
  renderVideoViewerTransform();
}

function syncViewerBodyState() {
  if (imageViewerState.open || videoViewerState.open) {
    document.body.classList.add("viewer-open");
  } else {
    document.body.classList.remove("viewer-open");
  }
}

function closeVideoViewer() {
  const overlay = $("video-viewer-overlay");
  const player = $("video-viewer-player");
  const status = $("video-viewer-status");
  const canvas = $("video-viewer-canvas");
  if (!overlay || !player || !status) {
    return;
  }
  videoViewerState.open = false;
  videoViewerState.rootId = null;
  videoViewerState.path = null;
  videoViewerState.naturalWidth = 0;
  videoViewerState.naturalHeight = 0;
  videoViewerState.scale = 1;
  videoViewerState.offsetX = 0;
  videoViewerState.offsetY = 0;
  videoViewerState.fragmentMode = false;
  videoViewerState.pendingPan = false;
  videoViewerState.dragging = false;
  videoViewerState.statusNote = "";
  videoViewerState.hasInitialLayout = false;
  videoViewerState.fallbackUsed = false;
  videoViewerState.fallbackReloading = false;
  videoViewerState.fallbackSkipNextSeeking = false;
  hideVideoViewerSelection();
  player.pause();
  player.onloadedmetadata = null;
  player.onerror = null;
  player.onseeking = null;
  player.style.transform = "";
  player.removeAttribute("src");
  player.load();
  status.textContent = "";
  overlay.classList.add("hidden");
  if (canvas) {
    canvas.classList.remove("fragment-mode");
    canvas.classList.remove("panning");
  }
  syncViewerBodyState();
}

function buildVideoViewerPreviewUrl(rootId, path, startSec) {
  return buildApiUrl("/api/file/preview/video", {
    root_id: rootId,
    path,
    start_sec: Number.isFinite(startSec) ? Number(startSec).toFixed(3) : "0.000",
    width: 960,
    video_bitrate_kbps: 1800,
    audio_bitrate_kbps: 128,
  });
}

function closeImageViewer() {
  const overlay = $("image-viewer-overlay");
  const img = $("image-viewer-img");
  const canvas = $("image-viewer-canvas");
  if (!overlay || !img || !canvas) {
    return;
  }
  imageViewerState.open = false;
  imageViewerState.path = null;
  imageViewerState.rootId = null;
  imageViewerState.naturalWidth = 0;
  imageViewerState.naturalHeight = 0;
  imageViewerState.scale = 1;
  imageViewerState.offsetX = 0;
  imageViewerState.offsetY = 0;
  imageViewerState.fragmentMode = false;
  imageViewerState.dragging = false;
  hideImageViewerSelection();
  overlay.classList.add("hidden");
  canvas.classList.remove("fragment-mode");
  canvas.classList.remove("panning");
  img.onload = null;
  img.onerror = null;
  img.removeAttribute("src");
  syncViewerBodyState();
}

function openImageViewer(rootId, path, name) {
  if (videoViewerState.open) {
    closeVideoViewer();
  }
  const overlay = $("image-viewer-overlay");
  const img = $("image-viewer-img");
  const status = $("viewer-status");
  if (!overlay || !img || !status) {
    throw new Error("Viewer controls are missing in DOM");
  }
  imageViewerState.open = true;
  imageViewerState.rootId = Number(rootId);
  imageViewerState.path = path;
  imageViewerState.fragmentMode = false;
  imageViewerState.dragging = false;
  hideImageViewerSelection();
  overlay.classList.remove("hidden");
  syncViewerBodyState();
  status.textContent = t("loading_file_details");
  img.alt = name || path || "image";

  img.onload = () => {
    imageViewerState.naturalWidth = img.naturalWidth || 0;
    imageViewerState.naturalHeight = img.naturalHeight || 0;
    fitImageViewerToScreen();
  };
  img.onerror = () => {
    status.textContent = t("file_preview_failed");
  };
  const src = buildApiUrl("/api/file/view/image", {
    root_id: rootId,
    path,
    t: Date.now(),
  });
  img.src = src;
}

function openVideoViewer(rootId, path, name) {
  if (imageViewerState.open) {
    closeImageViewer();
  }
  const overlay = $("video-viewer-overlay");
  const player = $("video-viewer-player");
  const status = $("video-viewer-status");
  if (!overlay || !player || !status) {
    throw new Error("Video viewer controls are missing in DOM");
  }
  videoViewerState.open = true;
  videoViewerState.rootId = Number(rootId);
  videoViewerState.path = path;
  videoViewerState.naturalWidth = 0;
  videoViewerState.naturalHeight = 0;
  videoViewerState.scale = 1;
  videoViewerState.offsetX = 0;
  videoViewerState.offsetY = 0;
  videoViewerState.fragmentMode = false;
  videoViewerState.pendingPan = false;
  videoViewerState.dragging = false;
  videoViewerState.statusNote = t("video_viewer_status_loading");
  videoViewerState.hasInitialLayout = false;
  videoViewerState.fallbackUsed = false;
  videoViewerState.fallbackReloading = false;
  videoViewerState.fallbackSkipNextSeeking = false;
  hideVideoViewerSelection();
  overlay.classList.remove("hidden");
  syncViewerBodyState();
  updateVideoViewerStatus();
  player.title = name || path || "video";

  const sourceUrl = buildApiUrl("/api/file/view/video", {
    root_id: rootId,
    path,
    t: Date.now(),
  });
  const fallbackUrl = buildVideoViewerPreviewUrl(rootId, path, 0);

  const restartFallbackFrom = (startSec, autoplay) => {
    if (!videoViewerState.open || !videoViewerState.fallbackUsed) {
      return;
    }
    videoViewerState.fallbackReloading = true;
    videoViewerState.fallbackSkipNextSeeking = true;
    player.src = buildVideoViewerPreviewUrl(rootId, path, startSec);
    player.load();
    player.addEventListener(
      "loadedmetadata",
      () => {
        videoViewerState.fallbackReloading = false;
        if (autoplay) {
          void player.play().catch(() => {});
        }
      },
      { once: true }
    );
    player.addEventListener(
      "error",
      () => {
        videoViewerState.fallbackReloading = false;
        videoViewerState.statusNote = t("video_viewer_status_error");
        updateVideoViewerStatus();
      },
      { once: true }
    );
  };

  player.onloadedmetadata = () => {
    videoViewerState.naturalWidth = player.videoWidth || videoViewerState.naturalWidth;
    videoViewerState.naturalHeight = player.videoHeight || videoViewerState.naturalHeight;
    if (!videoViewerState.hasInitialLayout) {
      fitVideoViewerToScreen();
      videoViewerState.hasInitialLayout = true;
    } else {
      renderVideoViewerTransform();
    }
    videoViewerState.statusNote = videoViewerState.fallbackUsed
      ? `${t("video_viewer_status_fallback")} ${t("file_preview_video_seek_hint")}`.trim()
      : t("video_viewer_status_ready");
    updateVideoViewerStatus();
  };
  player.onseeking = () => {
    if (!videoViewerState.fallbackUsed || videoViewerState.fallbackReloading) {
      return;
    }
    if (videoViewerState.fallbackSkipNextSeeking) {
      videoViewerState.fallbackSkipNextSeeking = false;
      return;
    }
    const target = Number(player.currentTime);
    if (!Number.isFinite(target) || target < 0.2) {
      return;
    }
    restartFallbackFrom(target, !player.paused);
  };
  player.onerror = () => {
    if (videoViewerState.fallbackReloading) {
      return;
    }
    if (!videoViewerState.fallbackUsed) {
      videoViewerState.fallbackUsed = true;
      videoViewerState.statusNote = t("video_viewer_status_loading");
      updateVideoViewerStatus();
      player.src = fallbackUrl;
      player.load();
      void player.play().catch(() => {});
      return;
    }
    videoViewerState.statusNote = t("video_viewer_status_error");
    updateVideoViewerStatus();
  };
  player.src = sourceUrl;
  player.load();
  void player.play().catch(() => {});
}

function clientToViewerCanvas(clientX, clientY) {
  const canvas = $("image-viewer-canvas");
  if (!canvas) {
    return null;
  }
  const rect = canvas.getBoundingClientRect();
  return {
    x: clientX - rect.left,
    y: clientY - rect.top,
    width: rect.width,
    height: rect.height,
  };
}

function clientToVideoViewerCanvas(clientX, clientY) {
  const canvas = $("video-viewer-canvas");
  if (!canvas) {
    return null;
  }
  const rect = canvas.getBoundingClientRect();
  return {
    x: clientX - rect.left,
    y: clientY - rect.top,
    width: rect.width,
    height: rect.height,
  };
}

function initImageViewer() {
  const overlay = $("image-viewer-overlay");
  const canvas = $("image-viewer-canvas");
  const selection = $("image-viewer-selection");
  const zoomInBtn = $("viewer-zoom-in-btn");
  const zoomOutBtn = $("viewer-zoom-out-btn");
  const zoom100Btn = $("viewer-zoom-100-btn");
  const fitBtn = $("viewer-fit-btn");
  const fragmentBtn = $("viewer-fragment-btn");
  const closeBtn = $("viewer-close-btn");
  if (!overlay || !canvas || !selection || !zoomInBtn || !zoomOutBtn || !zoom100Btn || !fitBtn || !fragmentBtn || !closeBtn) {
    return;
  }

  const updateSelectionBox = (x1, y1, x2, y2) => {
    const left = Math.min(x1, x2);
    const top = Math.min(y1, y2);
    const width = Math.abs(x2 - x1);
    const height = Math.abs(y2 - y1);
    selection.style.left = `${left}px`;
    selection.style.top = `${top}px`;
    selection.style.width = `${width}px`;
    selection.style.height = `${height}px`;
  };

  zoomInBtn.onclick = () => applyImageViewerScale(imageViewerState.scale * 1.25);
  zoomOutBtn.onclick = () => applyImageViewerScale(imageViewerState.scale / 1.25);
  zoom100Btn.onclick = () => setImageViewerScale100();
  fitBtn.onclick = () => fitImageViewerToScreen();
  fragmentBtn.onclick = () => {
    setImageViewerFragmentMode(!imageViewerState.fragmentMode);
  };
  closeBtn.onclick = () => closeImageViewer();
  overlay.onclick = (event) => {
    if (event.target === overlay) {
      closeImageViewer();
    }
  };

  canvas.addEventListener("pointerdown", (event) => {
    if (!imageViewerState.open || event.button !== 0) {
      return;
    }
    const point = clientToViewerCanvas(event.clientX, event.clientY);
    if (!point) {
      return;
    }
    if (imageViewerState.fragmentMode) {
      imageViewerState.selecting = true;
      imageViewerState.selectStartX = point.x;
      imageViewerState.selectStartY = point.y;
      selection.classList.remove("hidden");
      updateSelectionBox(point.x, point.y, point.x, point.y);
    } else {
      imageViewerState.dragging = true;
      imageViewerState.dragStartX = point.x;
      imageViewerState.dragStartY = point.y;
      imageViewerState.dragOriginOffsetX = imageViewerState.offsetX;
      imageViewerState.dragOriginOffsetY = imageViewerState.offsetY;
      updateImageViewerStatus();
    }
    canvas.setPointerCapture(event.pointerId);
  });

  canvas.addEventListener("pointermove", (event) => {
    if (imageViewerState.dragging) {
      const point = clientToViewerCanvas(event.clientX, event.clientY);
      if (!point) {
        return;
      }
      imageViewerState.offsetX =
        imageViewerState.dragOriginOffsetX + (point.x - imageViewerState.dragStartX);
      imageViewerState.offsetY =
        imageViewerState.dragOriginOffsetY + (point.y - imageViewerState.dragStartY);
      renderImageViewerTransform();
      return;
    }
    if (!imageViewerState.selecting) {
      return;
    }
    const point = clientToViewerCanvas(event.clientX, event.clientY);
    if (!point) {
      return;
    }
    updateSelectionBox(
      imageViewerState.selectStartX,
      imageViewerState.selectStartY,
      point.x,
      point.y
    );
  });

  const finishPointerAction = (event) => {
    const pointerId = event.pointerId;
    if (canvas.hasPointerCapture(pointerId)) {
      canvas.releasePointerCapture(pointerId);
    }

    if (imageViewerState.dragging) {
      imageViewerState.dragging = false;
      updateImageViewerStatus();
      return;
    }

    if (!imageViewerState.selecting) {
      return;
    }
    const point = clientToViewerCanvas(event.clientX, event.clientY);
    const startX = imageViewerState.selectStartX;
    const startY = imageViewerState.selectStartY;
    hideImageViewerSelection();
    if (!point) {
      return;
    }
    const left = Math.min(startX, point.x);
    const top = Math.min(startY, point.y);
    const width = Math.abs(point.x - startX);
    const height = Math.abs(point.y - startY);
    if (width < 10 || height < 10) {
      return;
    }
    zoomImageViewerToSelection(left, top, width, height);
  };

  canvas.addEventListener("pointerup", finishPointerAction);
  canvas.addEventListener("pointercancel", finishPointerAction);
  canvas.addEventListener(
    "wheel",
    (event) => {
      if (!imageViewerState.open) {
        return;
      }
      event.preventDefault();
      const point = clientToViewerCanvas(event.clientX, event.clientY);
      if (!point) {
        return;
      }
      const factor = Math.exp((-event.deltaY * 0.0015));
      applyImageViewerScale(imageViewerState.scale * factor, point.x, point.y);
    },
    { passive: false }
  );
}

function initVideoViewer() {
  const overlay = $("video-viewer-overlay");
  const canvas = $("video-viewer-canvas");
  const selection = $("video-viewer-selection");
  const zoomInBtn = $("video-viewer-zoom-in-btn");
  const zoomOutBtn = $("video-viewer-zoom-out-btn");
  const zoom100Btn = $("video-viewer-zoom-100-btn");
  const fitBtn = $("video-viewer-fit-btn");
  const fragmentBtn = $("video-viewer-fragment-btn");
  const closeBtn = $("video-viewer-close-btn");
  if (!overlay || !canvas || !selection || !zoomInBtn || !zoomOutBtn || !zoom100Btn || !fitBtn || !fragmentBtn || !closeBtn) {
    return;
  }

  const updateSelectionBox = (x1, y1, x2, y2) => {
    const left = Math.min(x1, x2);
    const top = Math.min(y1, y2);
    const width = Math.abs(x2 - x1);
    const height = Math.abs(y2 - y1);
    selection.style.left = `${left}px`;
    selection.style.top = `${top}px`;
    selection.style.width = `${width}px`;
    selection.style.height = `${height}px`;
  };

  zoomInBtn.onclick = () => applyVideoViewerScale(videoViewerState.scale * 1.25);
  zoomOutBtn.onclick = () => applyVideoViewerScale(videoViewerState.scale / 1.25);
  zoom100Btn.onclick = () => setVideoViewerScale100();
  fitBtn.onclick = () => fitVideoViewerToScreen();
  fragmentBtn.onclick = () => {
    setVideoViewerFragmentMode(!videoViewerState.fragmentMode);
  };
  closeBtn.onclick = () => closeVideoViewer();
  overlay.onclick = (event) => {
    if (event.target === overlay) {
      closeVideoViewer();
    }
  };

  canvas.addEventListener("pointerdown", (event) => {
    if (!videoViewerState.open) {
      return;
    }
    if (event.button !== 0) {
      return;
    }
    const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
    if (!point) {
      return;
    }
    if (videoViewerState.fragmentMode) {
      videoViewerState.selecting = true;
      videoViewerState.selectStartX = point.x;
      videoViewerState.selectStartY = point.y;
      selection.classList.remove("hidden");
      updateSelectionBox(point.x, point.y, point.x, point.y);
    } else {
      if (isPointInVideoViewerControlZone(point)) {
        return;
      }
      videoViewerState.pendingPan = true;
      videoViewerState.dragStartX = point.x;
      videoViewerState.dragStartY = point.y;
      videoViewerState.dragOriginOffsetX = videoViewerState.offsetX;
      videoViewerState.dragOriginOffsetY = videoViewerState.offsetY;
    }
    canvas.setPointerCapture(event.pointerId);
  });

  canvas.addEventListener("pointermove", (event) => {
    if (videoViewerState.pendingPan) {
      const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
      if (!point) {
        return;
      }
      const dx = point.x - videoViewerState.dragStartX;
      const dy = point.y - videoViewerState.dragStartY;
      if (Math.hypot(dx, dy) < VIDEO_VIEWER_PAN_START_DISTANCE) {
        return;
      }
      videoViewerState.pendingPan = false;
      videoViewerState.dragging = true;
      updateVideoViewerStatus();
    }
    if (videoViewerState.dragging) {
      const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
      if (!point) {
        return;
      }
      videoViewerState.offsetX =
        videoViewerState.dragOriginOffsetX + (point.x - videoViewerState.dragStartX);
      videoViewerState.offsetY =
        videoViewerState.dragOriginOffsetY + (point.y - videoViewerState.dragStartY);
      renderVideoViewerTransform();
      return;
    }
    if (!videoViewerState.selecting) {
      return;
    }
    const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
    if (!point) {
      return;
    }
    updateSelectionBox(
      videoViewerState.selectStartX,
      videoViewerState.selectStartY,
      point.x,
      point.y
    );
  });

  const finishPointerAction = (event) => {
    const pointerId = event.pointerId;
    if (canvas.hasPointerCapture(pointerId)) {
      canvas.releasePointerCapture(pointerId);
    }

    if (videoViewerState.pendingPan) {
      videoViewerState.pendingPan = false;
      return;
    }

    if (videoViewerState.dragging) {
      videoViewerState.dragging = false;
      updateVideoViewerStatus();
      return;
    }

    if (!videoViewerState.selecting) {
      return;
    }
    const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
    const startX = videoViewerState.selectStartX;
    const startY = videoViewerState.selectStartY;
    hideVideoViewerSelection();
    if (!point) {
      return;
    }
    const left = Math.min(startX, point.x);
    const top = Math.min(startY, point.y);
    const width = Math.abs(point.x - startX);
    const height = Math.abs(point.y - startY);
    if (width < 10 || height < 10) {
      return;
    }
    zoomVideoViewerToSelection(left, top, width, height);
  };

  canvas.addEventListener("pointerup", finishPointerAction);
  canvas.addEventListener("pointercancel", finishPointerAction);
  canvas.addEventListener(
    "wheel",
    (event) => {
      if (!videoViewerState.open) {
        return;
      }
      event.preventDefault();
      const point = clientToVideoViewerCanvas(event.clientX, event.clientY);
      if (!point) {
        return;
      }
      const factor = Math.exp(-event.deltaY * 0.0015);
      applyVideoViewerScale(videoViewerState.scale * factor, point.x, point.y);
    },
    { passive: false }
  );
}

function createFilePreviewNode(details) {
  if (!details || !details.root_id || !details.path) {
    return null;
  }
  const mime = String(details.mime || "").toLowerCase();
  const container = document.createElement("div");
  container.className = "file-preview-container";

  if (mime.startsWith("image/")) {
    const note = document.createElement("div");
    note.className = "file-preview-note";
    note.textContent = t("file_preview_loading");
    container.appendChild(note);

    const previewUrl = buildApiUrl("/api/file/preview/image", {
      root_id: details.root_id,
      path: details.path,
      width: 420,
      height: 280,
      quality: 45,
    });
    fetch(previewUrl)
      .then(async (response) => {
        if (!response.ok) {
          const text = await response.text();
          throw new Error(extractApiErrorMessage(text) || `HTTP ${response.status}`);
        }
        return response.blob();
      })
      .then((blob) => {
        container.innerHTML = "";
        const img = document.createElement("img");
        img.className = "file-preview-image";
        img.alt = details.name || details.path || "preview";
        img.loading = "lazy";
        img.src = URL.createObjectURL(blob);
        container.appendChild(img);
      })
      .catch((err) => {
        note.textContent = `${t("file_preview_failed")} ${extractApiErrorMessage(err.message)}`.trim();
        note.classList.add("file-preview-error");
      });
    return container;
  }

  if (mime.startsWith("video/")) {
    const video = document.createElement("video");
    video.className = "file-preview-video";
    video.controls = true;
    video.preload = "metadata";
    const note = document.createElement("div");
    note.className = "file-preview-note";
    note.textContent = t("file_preview_video_seek_hint");

    const buildVideoUrl = (startSec) =>
      buildApiUrl("/api/file/preview/video", {
        root_id: details.root_id,
        path: details.path,
        start_sec: Number.isFinite(startSec) ? Number(startSec).toFixed(3) : "0.000",
        width: 640,
        video_bitrate_kbps: 700,
        audio_bitrate_kbps: 96,
      });

    let reloadingBySeek = false;
    let skipNextSeeking = false;
    const restartFrom = (startSec, autoplay) => {
      reloadingBySeek = true;
      skipNextSeeking = true;
      video.src = buildVideoUrl(startSec);
      video.load();
      const done = () => {
        reloadingBySeek = false;
        if (autoplay) {
          void video.play().catch(() => {});
        }
      };
      video.addEventListener("loadedmetadata", done, { once: true });
      video.addEventListener("error", () => {
        reloadingBySeek = false;
      }, { once: true });
    };

    video.addEventListener("seeking", () => {
      if (reloadingBySeek) {
        return;
      }
      if (skipNextSeeking) {
        skipNextSeeking = false;
        return;
      }
      const target = Number(video.currentTime);
      if (!Number.isFinite(target) || target < 0.2) {
        return;
      }
      restartFrom(target, previewAutostart || !video.paused);
    });

    video.addEventListener("error", () => {
      note.textContent = t("file_preview_failed");
      note.classList.add("file-preview-error");
    });

    const checkUrl = buildApiUrl("/api/file/preview/video/check", {
      root_id: details.root_id,
      path: details.path,
    });
    fetch(checkUrl)
      .then(async (response) => {
        if (!response.ok) {
          const text = await response.text();
          throw new Error(extractApiErrorMessage(text) || `HTTP ${response.status}`);
        }
      })
      .then(() => {
        if (previewAutostart) {
          video.addEventListener("loadedmetadata", () => {
            void video.play().catch(() => {});
          }, { once: true });
        }
        video.src = buildVideoUrl(0);
      })
      .catch((err) => {
        note.textContent = `${t("file_preview_failed")} ${extractApiErrorMessage(err.message)}`.trim();
        note.classList.add("file-preview-error");
      });

    container.appendChild(video);
    container.appendChild(note);
    return container;
  }

  const unsupported = document.createElement("div");
  unsupported.className = "file-preview-note";
  unsupported.textContent = t("file_preview_not_available");
  container.appendChild(unsupported);
  return container;
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
  const previewNode = createFilePreviewNode(details);
  if (previewNode) {
    panel.appendChild(previewNode);
  }

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
  if (selectedRowType !== "file" || selectedRowPath !== path) {
    return;
  }
  renderFileDetails(details);
}

function scrollSelectedRowIntoView() {
  if (!selectedRowPath || !selectedRowType) {
    return;
  }
  const body = $("files-table-body");
  if (!body) {
    return;
  }
  const rows = body.querySelectorAll("tr[data-file-path][data-file-type]");
  rows.forEach((row) => {
    if (row.dataset.filePath === selectedRowPath && row.dataset.fileType === selectedRowType) {
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
  setSelectionFromRow(item);
  setFilesSelectionInfo(selectionInfoForRow(item));
  renderFilesTable();
  if (selectedDirContext && isFileRow(item)) {
    loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
      setFileDetailsPlaceholder(t("file_details_error"));
    });
  } else {
    setFileDetailsPlaceholder(t("file_details_placeholder"));
  }
  if (ensureVisible) {
    scrollSelectedRowIntoView();
  }
}

function moveFileSelection(step) {
  const rows = getSortedCurrentFiles();
  if (!rows.length) {
    return;
  }
  const currentIndex = rows.findIndex(
    (item) => item.path === selectedRowPath && item.type === selectedRowType
  );
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

async function copySelectedRowPath() {
  const item = getSelectedRow();
  if (!item || !item.path || isUpRow(item)) {
    return false;
  }
  return tryCopyToClipboard(item.path);
}

async function activateSelectedEntry() {
  const item = getSelectedRow();
  if (!item) {
    return;
  }
  if (isFileRow(item)) {
    await activateFile(item);
    return;
  }
  if ((isDirRow(item) || isUpRow(item)) && selectedDirContext) {
    await selectDirectory(selectedDirContext.rootId, item.path);
  }
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
  if (!item || !isFileRow(item)) {
    return;
  }
  setSelectionFromRow(item);
  renderFilesTable();
  const copied = await tryCopyToClipboard(item.path);
  if (copied) {
    setFilesSelectionInfo(t("file_path_copied", { path: item.path }));
  } else {
    setFilesSelectionInfo(t("file_activated", { path: item.path }));
  }
}

async function openFileByDoubleClick(item) {
  if (!item || !isFileRow(item)) {
    return;
  }
  if (!selectedDirContext) {
    await activateFile(item);
    return;
  }
  try {
    const details = await getFileDetails(selectedDirContext.rootId, item.path);
    if (details && (isImageMime(details.mime) || isImageName(item.name))) {
      openImageViewer(selectedDirContext.rootId, item.path, item.name);
      return;
    }
    if (details && (isVideoMime(details.mime) || isVideoName(item.name))) {
      openVideoViewer(selectedDirContext.rootId, item.path, item.name);
      return;
    }
  } catch {
    // fallback to default file activation
  }
  await activateFile(item);
}

function renderFilesTable() {
  const body = $("files-table-body");
  body.innerHTML = "";

  if (
    selectedRowPath &&
    selectedRowType &&
    !currentFiles.some((item) => item.path === selectedRowPath && item.type === selectedRowType)
  ) {
    selectedRowPath = null;
    selectedRowType = null;
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
    tr.dataset.fileType = item.type;
    if (item.path === selectedRowPath && item.type === selectedRowType) {
      tr.classList.add("selected");
    }
    tr.onclick = () => {
      setSelectionFromRow(item);
      setFilesSelectionInfo(selectionInfoForRow(item));
      renderFilesTable();
      if (selectedDirContext && isFileRow(item)) {
        loadAndRenderFileDetails(selectedDirContext.rootId, item.path).catch(() => {
          setFileDetailsPlaceholder(t("file_details_error"));
        });
      } else {
        setFileDetailsPlaceholder(t("file_details_placeholder"));
      }
    };
    tr.ondblclick = () => {
      if (selectedDirContext && (isDirRow(item) || isUpRow(item))) {
        selectDirectory(selectedDirContext.rootId, item.path).catch((err) => {
          alert(t("err_open_directory", { message: err.message }));
        });
        return;
      }
      openFileByDoubleClick(item).catch((err) => {
        if (isFileRow(item)) {
          alert(t("viewer_open_failed", { message: err.message }));
          return;
        }
        setFilesSelectionInfo(selectionInfoForRow(item));
      });
    };

    const name = document.createElement("td");
    if (isDirRow(item)) {
      name.textContent = `${item.name}/`;
    } else {
      name.textContent = item.name;
    }
    tr.appendChild(name);

    const size = document.createElement("td");
    if (isUpRow(item)) {
      size.textContent = "";
    } else if (Number.isFinite(Number(item.size))) {
      size.textContent = formatSize(item.size);
    } else {
      size.textContent = "";
    }
    tr.appendChild(size);

    const mtime = document.createElement("td");
    if (isUpRow(item)) {
      mtime.textContent = "";
    } else {
      mtime.textContent = formatDateTime(item.mtime);
    }
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
  const rootPath = normalizePath(data.rootPath || dirPath);
  const currentPath = normalizePath(data.dirPath || dirPath);
  const rows = [];
  if (currentPath !== rootPath) {
    const parentPath = normalizePath(getParentPath(currentPath));
    rows.push({
      name: t("parent_dir_name"),
      path: parentPath,
      type: "up",
      size: null,
      mtime: null,
    });
  }
  rows.push(...(data.dirs || []));
  rows.push(...(data.files || []));

  selectedDirContext = {
    rootId: Number(rootId),
    rootPath,
    dirPath: currentPath,
  };
  selectedDirKey = treeKey(rootId, selectedDirContext.dirPath);
  selectedRowPath = null;
  selectedRowType = null;
  currentFiles = rows;
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
  selectedRowPath = null;
  selectedRowType = null;
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

function applyRuntimeSettingsToForm(scanner) {
  if (!scanner || typeof scanner !== "object") {
    return;
  }
  if ($("hash-mode-select")) $("hash-mode-select").value = String(scanner.hash_mode || "auto");
  if ($("hash-threshold-input")) $("hash-threshold-input").value = String(scanner.hash_sample_threshold_mb ?? 256);
  if ($("hash-chunk-input")) $("hash-chunk-input").value = String(scanner.hash_sample_chunk_mb ?? 4);
  if ($("ffprobe-timeout-input")) $("ffprobe-timeout-input").value = String(scanner.ffprobe_timeout_sec ?? 8);
  if ($("ffprobe-analyze-input"))
    $("ffprobe-analyze-input").value = String(scanner.ffprobe_analyze_duration_us ?? 2000000);
  if ($("ffprobe-probesize-input"))
    $("ffprobe-probesize-input").value = String(scanner.ffprobe_probesize_bytes ?? 5000000);
}

function collectRuntimeSettingsFromForm() {
  const hashMode = $("hash-mode-select");
  const hashThreshold = $("hash-threshold-input");
  const hashChunk = $("hash-chunk-input");
  const ffprobeTimeout = $("ffprobe-timeout-input");
  const ffprobeAnalyze = $("ffprobe-analyze-input");
  const ffprobeProbeSize = $("ffprobe-probesize-input");
  if (!hashMode || !hashThreshold || !hashChunk || !ffprobeTimeout || !ffprobeAnalyze || !ffprobeProbeSize) {
    throw new Error("Runtime settings controls are not available in DOM");
  }
  return {
    hash_mode: hashMode.value,
    hash_sample_threshold_mb: Number(hashThreshold.value),
    hash_sample_chunk_mb: Number(hashChunk.value),
    ffprobe_timeout_sec: Number(ffprobeTimeout.value),
    ffprobe_analyze_duration_us: Number(ffprobeAnalyze.value),
    ffprobe_probesize_bytes: Number(ffprobeProbeSize.value),
  };
}

async function refreshRuntimeSettings() {
  const data = await api("/api/settings");
  applyRuntimeSettingsToForm(data.scanner || {});
  setRuntimeSettingsStatus("");
}

async function saveRuntimeSettings({ resetDefaults = false } = {}) {
  const payload = resetDefaults ? { reset_defaults: true } : collectRuntimeSettingsFromForm();
  const data = await api("/api/settings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  applyRuntimeSettingsToForm(data.scanner || {});
  setRuntimeSettingsStatus(resetDefaults ? t("runtime_settings_reset") : t("runtime_settings_saved"));
  await refreshState().catch(() => {});
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
  const currentFileNode = $("scan-current-file");
  if (currentFileNode) {
    currentFileNode.textContent = status.current_file
      ? t("status_current_file", { path: status.current_file })
      : t("status_current_file_none");
  }

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
  setRuntimeSettingsControlsDisabled(scanActive);
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
  const previewAutostartInput = $("preview-autostart-input");
  if (previewAutostartInput) {
    previewAutostartInput.onchange = (event) => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) {
        return;
      }
      applyPreviewAutostartSetting(target.checked, { persist: true, rerender: true });
    };
  }
  $("language-select").onchange = async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLSelectElement)) {
      return;
    }
    setLanguage(target.value);
    updateSortButtons();
    renderFilesTable();
    if (selectedDirContext && selectedRowPath && selectedRowType === "file") {
      const key = `${String(selectedDirContext.rootId)}:${selectedRowPath}`;
      const cached = fileDetailsCache.get(key);
      if (cached) {
        renderFileDetails(cached);
      } else {
        await loadAndRenderFileDetails(selectedDirContext.rootId, selectedRowPath).catch(() => {
          setFileDetailsPlaceholder(t("file_details_error"));
        });
      }
      setFilesSelectionInfo(t("file_selected", { path: selectedRowPath }));
    } else {
      setFileDetailsPlaceholder(t("file_details_placeholder"));
      if (!selectedRowPath || !selectedRowType) {
        setFilesSelectionInfo(t("files_selection_default"));
      } else {
        const selected = getSelectedRow();
        if (selected) {
          setFilesSelectionInfo(selectionInfoForRow(selected));
        }
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
  const saveRuntimeBtn = $("save-runtime-settings-btn");
  if (saveRuntimeBtn) {
    saveRuntimeBtn.onclick = async () => {
      try {
        await saveRuntimeSettings({ resetDefaults: false });
      } catch (err) {
        setRuntimeSettingsStatus(t("err_settings_save_failed", { message: err.message }), true);
      }
    };
  }
  const resetRuntimeBtn = $("reset-runtime-settings-btn");
  if (resetRuntimeBtn) {
    resetRuntimeBtn.onclick = async () => {
      try {
        await saveRuntimeSettings({ resetDefaults: true });
      } catch (err) {
        setRuntimeSettingsStatus(t("err_settings_save_failed", { message: err.message }), true);
      }
    };
  }
  $("state-refresh-btn").onclick = async () => {
    try {
      await refreshState();
    } catch (err) {
      alert(t("err_state_refresh_failed", { message: err.message }));
    }
  };

  document.addEventListener("keydown", (event) => {
    if (imageViewerState.open || videoViewerState.open) {
      if (event.key === "Escape") {
        event.preventDefault();
        if (imageViewerState.open) {
          closeImageViewer();
        }
        if (videoViewerState.open) {
          closeVideoViewer();
        }
      }
      return;
    }
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
      const selected = getSelectedRow();
      if (!selected || isUpRow(selected)) {
        setFilesSelectionInfo(t("select_file_first"));
        return;
      }
      copySelectedRowPath().then((ok) => {
        if (ok) {
          setFilesSelectionInfo(t("file_path_copied", { path: selected.path }));
          return;
        }
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
      activateSelectedEntry().catch(() => {
        setFilesSelectionInfo(t("file_action_failed"));
      });
    }
  });
}

async function bootstrap() {
  initLanguage();
  applyPreviewAutostartSetting(readPreviewAutostartSetting(), { persist: false, rerender: false });
  initBrowserPaneResize();
  initImageViewer();
  initVideoViewer();
  bindActions();
  updateSortButtons();
  await refreshRoots().catch((err) => {
    console.error("refreshRoots failed", err);
  });
  await refreshRuntimeSettings().catch((err) => {
    setRuntimeSettingsStatus(t("err_settings_load_failed", { message: err.message }), true);
  });
  await refreshStatus().catch((err) => {
    console.error("refreshStatus failed", err);
  });
  await refreshState().catch((err) => {
    console.error("refreshState failed", err);
  });
  await refreshTree().catch((err) => {
    console.error("refreshTree failed", err);
  });
  await refreshDuplicates().catch((err) => {
    console.error("refreshDuplicates failed", err);
  });
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
