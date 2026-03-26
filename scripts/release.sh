#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/release.sh <next-version> "<commit-message>" [--push] [--yes]

What it does:
  1. Reads the current committed APP_VERSION from HEAD
  2. Creates/refreshes local backup for that current version under backups/v<current-version>/
  3. Creates a Git tag v<current-version> if it does not already exist
  4. Updates APP_VERSION in index.html to <next-version>
  5. Runs static sanity checks
  6. Shows the required local smoke-test checklist
  7. Waits for confirmation (or skips prompt with --yes)
  8. Commits all changes
  9. Optionally pushes branch + tag with --push

Examples:
  ./scripts/release.sh 1.0.1-r3 "fix: improve calendar layout"
  ./scripts/release.sh 1.0.2 "release: cut official 1.0.2" --push
EOF
}

if [ "$#" -eq 1 ] && { [ "$1" = "-h" ] || [ "$1" = "--help" ]; }; then
  usage
  exit 0
fi

if [ "$#" -lt 2 ]; then
  usage
  exit 1
fi

NEXT_VERSION="$1"
COMMIT_MESSAGE="$2"
shift 2

PUSH=false
ASSUME_YES=false

for arg in "$@"; do
  case "$arg" in
    --push) PUSH=true ;;
    --yes) ASSUME_YES=true ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INDEX_HTML="$PROJECT_DIR/index.html"
CURRENT_BRANCH="$(git -C "$PROJECT_DIR" branch --show-current)"
HEAD_COMMIT="$(git -C "$PROJECT_DIR" rev-parse HEAD)"
HEAD_SHORT="$(git -C "$PROJECT_DIR" rev-parse --short HEAD)"
CURRENT_VERSION="$(git -C "$PROJECT_DIR" show HEAD:index.html | perl -ne "print \$1 if /const APP_VERSION = '([^']+)';/")"

if [ -z "$CURRENT_VERSION" ]; then
  echo "Failed to detect current APP_VERSION from HEAD:index.html" >&2
  exit 1
fi

if [ "$CURRENT_VERSION" = "$NEXT_VERSION" ]; then
  echo "Next version matches current version ($CURRENT_VERSION). Nothing to release." >&2
  exit 1
fi

CURRENT_TAG="v$CURRENT_VERSION"
BACKUP_DIR="$PROJECT_DIR/backups/v$CURRENT_VERSION"
mkdir -p "$BACKUP_DIR"

copy_from_head() {
  local file="$1"
  local target="$2"
  if git -C "$PROJECT_DIR" cat-file -e "HEAD:$file" 2>/dev/null; then
    git -C "$PROJECT_DIR" show "HEAD:$file" > "$target"
  fi
}

copy_from_head "index.html" "$BACKUP_DIR/index.html"
copy_from_head "README.md" "$BACKUP_DIR/README.md"
copy_from_head "VERSIONING.md" "$BACKUP_DIR/VERSIONING.md"

CURRENT_VERSION="$CURRENT_VERSION" HEAD_SHORT="$HEAD_SHORT" HEAD_COMMIT="$HEAD_COMMIT" NEXT_VERSION="$NEXT_VERSION" BACKUP_DIR="$BACKUP_DIR" python3 <<'PY'
import json
import os
from pathlib import Path
manifest = {
    "version": os.environ["CURRENT_VERSION"],
    "sourceCommit": os.environ["HEAD_SHORT"],
    "sourceCommitFull": os.environ["HEAD_COMMIT"],
    "createdAt": __import__('datetime').datetime.now(__import__('datetime').UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    "note": f"Backup captured from HEAD before releasing {os.environ['NEXT_VERSION']}"
}
backup_dir = Path(os.environ["BACKUP_DIR"])
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY

echo "[release] Local backup ready: $BACKUP_DIR"

if git -C "$PROJECT_DIR" rev-parse "$CURRENT_TAG" >/dev/null 2>&1; then
  echo "[release] Tag already exists: $CURRENT_TAG"
  TAG_CREATED=false
else
  git -C "$PROJECT_DIR" tag -a "$CURRENT_TAG" -m "Snapshot for version $CURRENT_VERSION before releasing $NEXT_VERSION" "$HEAD_COMMIT"
  echo "[release] Created tag: $CURRENT_TAG"
  TAG_CREATED=true
fi

INDEX_HTML="$INDEX_HTML" NEXT_VERSION="$NEXT_VERSION" python3 <<'PY'
from pathlib import Path
import os
import re
path = Path(os.environ['INDEX_HTML'])
text = path.read_text(encoding='utf-8')
next_version = os.environ['NEXT_VERSION']
new_text, count = re.subn(r"const APP_VERSION = '[^']+';", f"const APP_VERSION = '{next_version}';", text, count=1)
if count != 1:
    raise SystemExit('Failed to update APP_VERSION in index.html')
path.write_text(new_text, encoding='utf-8')
PY

echo "[release] Updated APP_VERSION -> $NEXT_VERSION"

INDEX_HTML="$INDEX_HTML" NEXT_VERSION="$NEXT_VERSION" python3 <<'PY'
from pathlib import Path
import os
text = Path(os.environ['INDEX_HTML']).read_text(encoding='utf-8')
next_version = os.environ['NEXT_VERSION']
checks = {
    'APP_VERSION updated': f"const APP_VERSION = '{next_version}';" in text,
    'versionInfo node exists': 'id="versionInfo"' in text,
    'version text binding exists': "document.getElementById('versionInfo').textContent" in text,
    'add project button exists': 'id="addProjectBtn"' in text,
    'save button exists': 'id="saveBtn"' in text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Static checks failed: ' + ', '.join(failed))
print('[release] Static checks passed')
PY

cat <<EOF

[release] Required local smoke test before commit:
  1. Open index.html (or start a local static server)
  2. Confirm the page shows version: $NEXT_VERSION
  3. Click "+ 添加项目"
  4. Create a test project
  5. Edit the test project
  6. Delete the test project
  7. Switch 列表 / 看板 / 日历
  8. Confirm 导出数据 / 导入备份 / 清空 are still visible
EOF

if [ "$ASSUME_YES" != true ]; then
  printf "\nType YES after local smoke test passes: "
  read -r CONFIRM
  if [ "$CONFIRM" != "YES" ]; then
    echo "Release aborted before commit. Backup/tag/version bump remain in working tree."
    exit 1
  fi
else
  echo "[release] --yes supplied: assuming local smoke test already passed"
fi

git -C "$PROJECT_DIR" add -A

git -C "$PROJECT_DIR" commit -m "$COMMIT_MESSAGE"
echo "[release] Commit created"

if [ "$PUSH" = true ]; then
  git -C "$PROJECT_DIR" push origin "$CURRENT_BRANCH"
  git -C "$PROJECT_DIR" push origin "$CURRENT_TAG"
  echo "[release] Pushed branch $CURRENT_BRANCH and ensured tag $CURRENT_TAG is on origin"
else
  echo "[release] Push skipped. Run git push origin $CURRENT_BRANCH manually when ready."
  echo "[release] Remember to push tag too: git push origin $CURRENT_TAG"
fi
