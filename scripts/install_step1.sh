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

echo "[1/7] Create venv: $VENV_PATH"
python3 -m venv "$VENV_PATH"

echo "[2/7] Install package"
"$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel
"$VENV_PATH/bin/pip" install -e "$ROOT_DIR"

echo "[3/7] Prepare env file: $ENV_FILE"
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

echo "[4/7] Prepare DB migrations"
"$VENV_PATH/bin/catalogic" db migrate --db "$DB_PATH"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "[5/7] systemctl not found; skip systemd setup"
  echo "Run manually:"
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-server\""
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-scanner\""
  echo "  source \"$ENV_FILE\" && \"$VENV_PATH/bin/catalogic-frontend\""
  exit 0
fi

echo "[5/7] Install systemd units (requires sudo)"
sudo cp "$ROOT_DIR/scripts/systemd/catalogic-backend.service" /etc/systemd/system/catalogic-backend.service
sudo cp "$ROOT_DIR/scripts/systemd/catalogic-scanner.service" /etc/systemd/system/catalogic-scanner.service
sudo cp "$ROOT_DIR/scripts/systemd/catalogic-frontend.service" /etc/systemd/system/catalogic-frontend.service
sudo sed -i "s|__WORKDIR__|$ROOT_DIR|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
sudo sed -i "s|__VENV__|$VENV_PATH|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
sudo sed -i "s|__ENV__|$ENV_FILE|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service
sudo sed -i "s|__USER__|$SERVICE_USER|g" /etc/systemd/system/catalogic-backend.service /etc/systemd/system/catalogic-scanner.service /etc/systemd/system/catalogic-frontend.service

echo "[6/7] Enable and start services"
sudo systemctl daemon-reload
sudo systemctl enable --now catalogic-backend.service
sudo systemctl enable --now catalogic-scanner.service
sudo systemctl enable --now catalogic-frontend.service

echo "[7/7] Services started"

echo "Done."
echo "Backend:  http://$API_HOST:$API_PORT"
echo "Frontend: http://$FRONTEND_HOST:$FRONTEND_PORT"
