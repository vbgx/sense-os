#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

cmd="${1:-}"
shift || true

case "$cmd" in
  migrate)   exec "$SCRIPT_DIR/migrate.sh" "$@" ;;
  seed)     exec "$SCRIPT_DIR/seed_verticals.sh" "$@" ;;
  flush-redis) exec "$SCRIPT_DIR/flush_redis.sh" "$@" ;;
  logs)
    svc="${1:-}"; [ -n "$svc" ] || die "Usage: $0 logs <service>"
    exec dc logs -f --tail=200 "$svc"
    ;;
  validate)  exec "$SCRIPT_DIR/validate_full_boot.sh" "$@" ;;
  bundle)    exec "$SCRIPT_DIR/bundle_scripts.sh" "$@" ;;
  *)
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  migrate         Alembic upgrade head"
    echo "  seed            Seed verticals"
    echo "  flush-redis     FLUSHALL (requires FORCE=1)"
    echo "  logs <service>  Follow docker compose logs"
    echo "  validate        Full boot validation"
    echo "  bundle          Generate scripts bundle md"
    exit 1
    ;;
esac
