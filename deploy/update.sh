#!/usr/bin/env bash
set -euo pipefail

# deploy/update.sh
# Jalan di tiap VM lewat cron (bukan dipanggil GitHub). Baca config dari
# .env di folder yang sama, lalu:
#   1. docker pull image terbaru dari Docker Hub
#   2. bandingin image ID lama vs baru
#   3. beda  -> stop+remove container lama, run container baru
#   4. sama  -> nggak ngapa-ngapain, exit

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
LOG_PREFIX="[update.sh $(date '+%Y-%m-%d %H:%M:%S')]"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "$LOG_PREFIX .env tidak ditemukan di $ENV_FILE. Copy dari .env.example dulu." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${IMAGE:?IMAGE belum diset di .env}"
: "${CONTAINER_NAME:?CONTAINER_NAME belum diset di .env}"
: "${HOST_PORT:?HOST_PORT belum diset di .env}"
: "${CONTAINER_PORT:?CONTAINER_PORT belum diset di .env}"

# ID image yang lagi dipakai container yang jalan sekarang (kalau ada).
OLD_ID="$(docker inspect --format='{{.Image}}' "$CONTAINER_NAME" 2>/dev/null || echo "")"

echo "$LOG_PREFIX Pull image terbaru: $IMAGE"
docker pull "$IMAGE" >/dev/null

NEW_ID="$(docker inspect --format='{{.Id}}' "$IMAGE")"

if [[ "$OLD_ID" == "$NEW_ID" ]]; then
  echo "$LOG_PREFIX Image sama, tidak ada perubahan. Exit."
  exit 0
fi

echo "$LOG_PREFIX Image baru terdeteksi ($OLD_ID -> $NEW_ID). Update container..."

docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  "$IMAGE" >/dev/null

echo "$LOG_PREFIX Container '$CONTAINER_NAME' jalan pakai image baru, port ${HOST_PORT}->${CONTAINER_PORT}."
