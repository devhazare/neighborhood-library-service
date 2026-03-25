#!/bin/bash
#
# Database backup script for Library Service
# Usage: ./backup_db.sh
#

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/library_db_$TIMESTAMP.sql"
DATABASE_URL="${DATABASE_URL:-postgresql://library:library@localhost:5432/library_db}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."
echo "Backup file: $BACKUP_FILE"

# Perform backup
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

echo "Backup completed: $BACKUP_FILE"

# Calculate file size
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup size: $SIZE"

# Clean up old backups (keep only last N days)
echo "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "library_db_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "library_db_*.sql.gz" | wc -l)
echo "Total backups in $BACKUP_DIR: $BACKUP_COUNT"

# Optional: Upload to S3 (uncomment if using AWS)
# if command -v aws &> /dev/null; then
#     S3_BUCKET="${S3_BUCKET:-library-backups}"
#     echo "Uploading to S3 bucket: $S3_BUCKET"
#     aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/$(basename $BACKUP_FILE)"
#     echo "Upload completed"
# fi

echo "Backup process finished successfully!"

