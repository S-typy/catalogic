#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${CATALOGIC_ENV_FILE:-$ROOT_DIR/.env}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$ENV_FILE"
  set +a
fi

VENV_PATH="${VENV_PATH:-$ROOT_DIR/.venv}"
DB_PATH="${CATALOGIC_DB_PATH:-$ROOT_DIR/data/catalogic.db}"
API_HOST="${CATALOGIC_HOST:-0.0.0.0}"
API_PORT="${CATALOGIC_PORT:-8080}"
FRONTEND_HOST="${CATALOGIC_FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${CATALOGIC_FRONTEND_PORT:-8081}"
API_BASE="${CATALOGIC_API_BASE:-http://127.0.0.1:$API_PORT}"
SERVICE_USER="${CATALOGIC_SERVICE_USER:-$USER}"

as_root() {
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    "$@"
    return
  fi
  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
    return
  fi
  echo "ERROR: root privileges required for: $*"
  echo "Install sudo or run installer as root."
  exit 1
}

if ! command -v ffprobe >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "[0/8] Installing ffprobe via apt (ffmpeg package)"
    as_root apt-get update -y
    as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y ffmpeg
    if ! command -v ffprobe >/dev/null 2>&1; then
      echo "ERROR: ffprobe was not installed successfully."
      exit 1
    fi
  else
    echo "[0/8] WARNING: ffprobe is not installed and apt-get is unavailable."
    echo "      Install ffprobe manually for video/audio metadata extraction."
  fi
else
  echo "[0/8] ffprobe already installed: $(command -v ffprobe)"
fi

echo "[1/8] Create venv: $VENV_PATH"
python3 -m venv "$VENV_PATH"

echo "[2/8] Install package"
"$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel
"$VENV_PATH/bin/pip" install -e "$ROOT_DIR"

echo "[3/8] Prepare env file: $ENV_FILE"
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<EOF
CATALOGIC_DB_PATH=$DB_PATH
CATALOGIC_HOST=$API_HOST
CATALOGIC_PORT=$API_PORT
CATALOGIC_FRONTEND_HOST=$FRONTEND_HOST
CATALOGIC_FRONTEND_PORT=$FRONTEND_PORT
CATALOGIC_API_BASE=$API_BASE
VENV_PATH=$VENV_PATH
CATALOGIC_SERVICE_USER=$SERVICE_USER
EOF
  echo "Created $ENV_FILE"
else
  echo "Using existing $ENV_FILE"
fi

echo "[4/8] Prepare DB migrations"
"$VENV_PATH/bin/catalogic" db migrate --db "$DB_PATH"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "[5/8] systemctl not found; skip systemd setup"
  echo "Run manually:"
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-server\""
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-scanner\""
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-frontend\""
  exit 0
fi

echo "[5/8] Install systemd units (requires sudo)"
as_root cp "$ROOT_DIR/scripts/systemd/catalogic-backend.service" /etc/systemd/system/catalogic-backend.service
as_root cp "$ROOT_DIR/scripts/systemd/catalogic-scanner.service" /etc/systemd/system/catalogic-scanner.service
as_root cp "$ROOT_DIR/scripts/systemd/catalogic-frontend.service" /etc/systemd/system/catalogic-frontend.service
as_root sed -i "s|__WORKDIR__|$ROOT_DIR|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
as_root sed -i "s|__VENV__|$VENV_PATH|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
as_root sed -i "s|__ENV__|$ENV_FILE|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
as_root sed -i "s|__USER__|$SERVICE_USER|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service

echo "[6/8] Enable and start services"
as_root systemctl daemon-reload
as_root systemctl enable --now catalogic-backend.service
as_root systemctl enable --now catalogic-scanner.service
as_root systemctl enable --now catalogic-frontend.service

echo "[7/8] Services started"

echo "[8/8] Runtime checks"
if command -v ffprobe >/dev/null 2>&1; then
  echo "ffprobe: $(command -v ffprobe)"
fi

echo "Done."
echo "Backend:  http://$API_HOST:$API_PORT"
echo "Frontend: http://$FRONTEND_HOST:$FRONTEND_PORT"
