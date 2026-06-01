#!/bin/bash
# Log rotation script for distributed storage infrastructure

LOG_DIR="./logs"
ARCHIVE_DIR="$LOG_DIR/archive"
MAX_SIZE=10485760  # 10MB
RETENTION_DAYS=7

echo "[INFO] Starting log rotation..."

# Create archive directory if it doesn't exist
mkdir -p $ARCHIVE_DIR

# Rotate logs larger than MAX_SIZE
for logfile in $LOG_DIR/*.log; do
    if [ -f "$logfile" ]; then
        size=$(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile" 2>/dev/null)
        
        if [ $size -gt $MAX_SIZE ]; then
            timestamp=$(date +%Y%m%d_%H%M%S)
            archivefile="$ARCHIVE_DIR/$(basename $logfile .log)_$timestamp.log"
            mv $logfile $archivefile
            gzip $archivefile
            echo "[INFO] Rotated and compressed: $archivefile.gz"
        fi
    fi
done

# Delete old archived logs
find $ARCHIVE_DIR -name "*.log.gz" -mtime +$RETENTION_DAYS -delete
echo "[INFO] Deleted logs older than $RETENTION_DAYS days"

echo "[INFO] Log rotation completed!"