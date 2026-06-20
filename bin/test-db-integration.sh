#!/usr/bin/env bash
#
# Run the database/ORM/API test suite end-to-end against REAL database engines
# (Postgres, MySQL, MariaDB) using throwaway docker containers.
#
# The normal unit suite (./bin/test.sh) runs against in-memory SQLite.  This
# runner points BOTH the app1 and auth connections at a real server (via the
# tests/integration/env/<backend>.env files) so the exact same schema, seeders
# and tests execute against each engine - exposing any dialect-specific gaps.
#
# Usage:
#   ./bin/test-db-integration.sh postgres
#   ./bin/test-db-integration.sh mysql
#   ./bin/test-db-integration.sh mariadb
#   ./bin/test-db-integration.sh all
#   KEEP_UP=1 ./bin/test-db-integration.sh postgres   # leave containers running
#
# Extra pytest args pass through after the backend, e.g.:
#   ./bin/test-db-integration.sh postgres tests/test_db/test_orm -x

set -e
base="$( cd "$(dirname "$0")" ; cd .. ; pwd -P )"; cd "$base"
intdir="$base/tests/integration"
compose="docker compose -f $intdir/docker-compose.yml"

# Which test paths run against the real database.
# These are the dialect-agnostic suites (portable assertions: sorted/set comparisons,
# ilike for case-insensitive matching, db-generated pks).  The broader unit suite under
# tests/test_db/test_orm contains some SQLite-specific assumptions (implicit row order,
# case-insensitive LIKE) and is intentionally NOT part of the default cross-db run.
DEFAULT_PATHS="tests/integration tests/test_db/test_dialects.py tests/test_db/test_orm/test_where_operators.py tests/test_db/test_orm/test_polymorphic_mutations.py tests/test_db/test_orm/test_multiple_many_includes.py tests/test_db/test_orm/test_insert_autopk.py tests/test_api"

backend="${1:-all}"; shift || true
extra_args="$@"

backends=()
case "$backend" in
  all) backends=(postgres mysql mariadb) ;;
  postgres|mysql|mariadb) backends=("$backend") ;;
  *) echo "Usage: $0 {postgres|mysql|mariadb|all} [pytest args]"; exit 1 ;;
esac

cleanup() {
  if [ -z "$KEEP_UP" ]; then
    echo ":: Tearing down integration databases ::"
    $compose down -v >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

overall=0
for be in "${backends[@]}"; do
  echo ""
  echo "################################################################################"
  echo "## Integration tests against: $be"
  echo "################################################################################"

  echo ":: Starting $be container ::"
  $compose up -d "$be"

  echo ":: Waiting for $be to become healthy ::"
  for i in $(seq 1 60); do
    status=$($compose ps --format '{{.Health}}' "$be" 2>/dev/null || echo "")
    [ "$status" = "healthy" ] && break
    sleep 2
  done
  if [ "$status" != "healthy" ]; then
    echo "ERROR: $be did not become healthy"; $compose logs "$be" | tail -30; overall=1; continue
  fi

  echo ":: Running tests against $be ::"
  set -a; source "$intdir/env/$be.env"; set +a
  export PYTHONPATH=./tests/apps
  if poetry run pytest --color=yes --log-level=WARNING -W ignore::DeprecationWarning \
      --ignore=tests/test_database ${extra_args:-$DEFAULT_PATHS}; then
    echo ":: $be PASSED ::"
  else
    echo ":: $be FAILED ::"; overall=1
  fi

  # Stop this backend before the next (unless keeping up)
  [ -z "$KEEP_UP" ] && $compose stop "$be" >/dev/null 2>&1 || true
done

exit $overall
