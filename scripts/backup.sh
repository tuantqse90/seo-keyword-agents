#!/bin/bash
# Database backup script for SEO Dashboard
# Usage: ./scripts/backup.sh
# Cron:  0 2 * * * /path/to/seo-keyword-agents/scripts/backup.sh

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/seo_dashboard_${TIMESTAMP}.sql.gz"

# Database config (from env or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-seo_dashboard}"
DB_USER="${POSTGRES_USER:-seo_user}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..."

# If running in Docker, use docker exec
if docker ps --format '{{.Names}}' | grep -q seo-postgres; then
    docker exec seo-postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
else
    PGPASSWORD="${POSTGRES_PASSWORD:-seo_password}" pg_dump \
        -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
fi

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date)] Backup complete: $BACKUP_FILE ($FILESIZE)"

# Clean old backups
DELETED=$(find "$BACKUP_DIR" -name "seo_dashboard_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    echo "[$(date)] Cleaned $DELETED old backup(s) (older than ${RETENTION_DAYS} days)"
fi

echo "[$(date)] Done. Active backups:"
ls -lh "$BACKUP_DIR"/seo_dashboard_*.sql.gz 2>/dev/null | tail -5
