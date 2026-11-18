#!/bin/sh
# Dump nocturne + rotation locale 7 jours.
# Déclenché par le timer systemd utilisateur eyesonme-backup.timer (03:00 UTC, Persistent=true).
# La machine n'a pas de cron : ne pas compter sur une entrée crontab.
set -eu
BACKUP_DIR="${BACKUP_DIR:-/home/ubuntu/EyesOnMe/backups}"
RETENTION_DAYS=7
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"
OUT="$BACKUP_DIR/eyesonme-$STAMP.dump"
trap 'rm -f "$OUT.tmp"' EXIT
docker exec eyesonme_db sh -c 'pg_dump -U eyesonme_owner -d "$POSTGRES_DB" -Fc' > "$OUT.tmp"
[ -s "$OUT.tmp" ] || { echo "dump vide" >&2; rm -f "$OUT.tmp"; exit 1; }
mv "$OUT.tmp" "$OUT"
find "$BACKUP_DIR" -name 'eyesonme-*.dump' -mtime +"$RETENTION_DAYS" -delete
echo "ok $OUT"
