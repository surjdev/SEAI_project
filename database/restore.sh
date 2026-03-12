#!/bin/bash
set -e

echo "Starting Restore Process..."

# --no-owner: Prevents trying to 'ALTER OWNER TO postgres'
# --no-privileges: Skips restoring access permissions (prevents similar errors)
# -O: Another way to say no-owner
pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --no-owner \
    --no-privileges \
    -c --if-exists \
    /docker-entrypoint-initdb.d/my_backup.dump

echo "Restore Finished!"