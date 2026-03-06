#!/bin/bash
# Database restore script for SEO Dashboard
# Usage: ./scripts/restore.sh backups/seo_dashboard_20260306.sql.gz

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh backups/seo_dashboard_*.sql.gz 2>/dev/null || echo "  No backups found in ./backups/"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File not found: $BACKUP_FILE"
    exit 1
fi

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-seo_dashboard}"
DB_USER="${POSTGRES_USER:-seo_user}"

echo "WARNING: This will overwrite the database '$DB_NAME' with data from:"
echo "  $BACKUP_FILE"
echo ""
read -p "Are you sure? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo "[$(date)] Restoring from $BACKUP_FILE..."

if docker ps --format '{{.Names}}' | grep -q seo-postgres; then
    gunzip -c "$BACKUP_FILE" | docker exec -i seo-postgres psql -U "$DB_USER" -d "$DB_NAME"
else
    PGPASSWORD="${POSTGRES_PASSWORD:-seo_password}" gunzip -c "$BACKUP_FILE" | \
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
fi

echo "[$(date)] Restore complete!"
