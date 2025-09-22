#!/bin/bash

# Backup PostgreSQL database
echo "Creating database backup..."

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

pg_dump $DATABASE_URL > $BACKUP_FILE

echo "Backup completed: $BACKUP_FILE"