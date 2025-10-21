#!/bin/bash
echo "Resetting DB from backup..."
mkdir -p app/server/db
cp app/server/db/backup.db app/server/db/database.db && echo "✓ DB reset" || { echo "✗ Failed"; exit 1; }
