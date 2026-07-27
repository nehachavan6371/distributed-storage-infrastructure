#!/bin/bash
# log_rotation.sh — Rotate and archive Docker container logs
# Usage: bash scripts/log_rotation.sh
# Recommended: Add to crontab → 0 0 * * * bash /path/to/log_rotation.sh

set -e

LOG_DIR="./logs"
ARCHIVE_DIR="./logs/archive"
MAX_LOG_SIZE_MB=50
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"

CONTAINERS=("coordinator" "storage-node-1" "storage-node-2" "storage-node-3")

echo "[$(date)] Starting log rotation..."

for CONTAINER in "${CONTAINERS[@]}"; do
    LOG_FILE="$LOG_DIR/${CONTAINER}.log"

    # Dump current container logs
    docker logs "$CONTAINER" > "$LOG_FILE" 2>&1 || echo "  Warning: Could not get logs for $CONTAINER"

    # Check log file size
    if [ -f "$LOG_FILE" ]; then
        SIZE_MB=$(du -m "$LOG_FILE" | cut -f1)
        if [ "$SIZE_MB" -ge "$MAX_LOG_SIZE_MB" ]; then
            ARCHIVE_FILE="$ARCHIVE_DIR/${CONTAINER}_${DATE}.log.gz"
            gzip -c "$LOG_FILE" > "$ARCHIVE_FILE"
            echo "" > "$LOG_FILE"
            echo "  Archived $CONTAINER logs → $ARCHIVE_FILE (${SIZE_MB}MB)"
        else
            echo "  $CONTAINER log OK (${SIZE_MB}MB)"
        fi
    fi
done

# Clean archives older than 30 days
find "$ARCHIVE_DIR" -name "*.log.gz" -mtime +30 -delete
echo "[$(date)] Log rotation complete."
