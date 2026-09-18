#!/bin/bash
BACKUP_DIR="/home/brifas/backups"
DATE=$(date +%Y%m%d)
KEEP_DAYS=30

mkdir -p "$BACKUP_DIR"

# SQLite database
cp /home/brifas/dashboard.db "$BACKUP_DIR/dashboard_$DATE.db"

# Config files
cp /home/brifas/frigate/config/config.yml "$BACKUP_DIR/frigate_config_$DATE.yml"
cp /home/brifas/backend/main.py "$BACKUP_DIR/main_py_$DATE.py"
cp /home/brifas/automation_engine.py "$BACKUP_DIR/automation_engine_$DATE.py"
cp /home/brifas/rak_reader.py "$BACKUP_DIR/rak_reader_$DATE.py"

# Delete backups older than 30 days
find "$BACKUP_DIR" -type f -mtime +$KEEP_DAYS -delete

echo "Backup complete: $DATE"
