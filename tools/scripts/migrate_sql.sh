#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

DIR="${DIR:-infra/sql}"
MODE="${MODE:-all}"          # all | list | file
FILE="${FILE:-}"             # used if MODE=file
DRY_RUN="${DRY_RUN:-0}"      # 1 => print only

apply_one() {
  local f="$1"
  [ -f "$REPO_ROOT/$f" ] || die "SQL file not found: $f"
  echo "==> applying $f"
  if [ "$DRY_RUN" = "1" ]; then
    return 0
  fi
  cat "$REPO_ROOT/$f" | dc_exec postgres psql -U postgres -d postgres
}

step "🗄️  SQL migrate (DIR=$DIR MODE=$MODE DRY_RUN=$DRY_RUN)"

case "$MODE" in
  list)
    (cd "$REPO_ROOT" && ls -1 "$DIR"/*.sql 2>/dev/null | sed "s|^$REPO_ROOT/||" ) || true
    exit 0
    ;;
  file)
    [ -n "$FILE" ] || die "MODE=file requires FILE=path/to.sql"
    apply_one "$FILE"
    ;;
  all)
    # sort ensures deterministic order
    while IFS= read -r f; do
      apply_one "$f"
    done < <(cd "$REPO_ROOT" && ls -1 "$DIR"/*.sql 2>/dev/null | sort | sed "s|^$REPO_ROOT/||")
    ;;
  *)
    die "Unknown MODE=$MODE (use: all|list|file)"
    ;;
esac

echo "✅ Migrations complete"
