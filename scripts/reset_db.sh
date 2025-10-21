#!/bin/bash

echo "Starting database reset..."

# Restore database from backup for testing
echo "Copying backup.db to database.db..."
cp app/server/db/backup.db app/server/db/database.db

if [ $? -eq 0 ]; then
    echo "✓ Database reset successfully completed"
else
    echo "✗ Error: Failed to reset database"
    exit 1
fi