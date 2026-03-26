#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <version> [note]" >&2
  exit 1
fi

VERSION="$1"
NOTE="${2:-manual backup}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups/v$VERSION"
COMMIT_HASH="$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$BACKUP_DIR"
cp "$PROJECT_DIR/index.html" "$BACKUP_DIR/index.html"
cp "$PROJECT_DIR/README.md" "$BACKUP_DIR/README.md"
[ -f "$PROJECT_DIR/VERSIONING.md" ] && cp "$PROJECT_DIR/VERSIONING.md" "$BACKUP_DIR/VERSIONING.md"

cat > "$BACKUP_DIR/manifest.json" <<EOF
{
  "version": "$VERSION",
  "sourceCommit": "$COMMIT_HASH",
  "createdAt": "$TIMESTAMP",
  "note": "$NOTE"
}
EOF

echo "Backup created: $BACKUP_DIR"
