#!/usr/bin/env bash
#
# Run the generic redis SERVICE test suite end-to-end against a REAL redis server
# using a throwaway docker container.
#
# This covers uvicore/redis (the connection helper + passthrough), NOT caching -
# see ./bin/test-cache-integration.sh for the redis cache backend.  Both runners
# use the same redis container and tests/integration/env/redis.env.
#
# The normal unit suite (./bin/test.sh) only checks that the service is wired up;
# this runner brings up a redis container, points the app1/cache redis connections
# at it, and exercises real redis commands through the service - mirroring how
# ./bin/test-integration.sh exercises the database layer against real engines.
#
# Usage:
#   ./bin/test-redis-integration.sh
#   KEEP_UP=1 ./bin/test-redis-integration.sh           # leave the redis container running
#   ./bin/test-redis-integration.sh tests/integration/test_redis_service.py -x   # extra pytest args
#
# When redis is unreachable the suite is written to SKIP rather than fail, so it
# is also safe to collect under the default ./bin/test.sh run.

set -e
base="$( cd "$(dirname "$0")" ; cd .. ; pwd -P )"; cd "$base"
intdir="$base/tests/integration"
compose="docker compose -f $intdir/docker-compose.yml"

DEFAULT_PATHS="tests/integration/test_redis_service.py"
extra_args="$@"

cleanup() {
  if [ -z "$KEEP_UP" ]; then
    echo ":: Tearing down integration redis ::"
    $compose down -v >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo ""
echo "################################################################################"
echo "## Redis service integration tests against: redis"
echo "################################################################################"

echo ":: Starting redis container ::"
$compose up -d redis

echo ":: Waiting for redis to become healthy ::"
status=""
for i in $(seq 1 60); do
  status=$($compose ps --format '{{.Health}}' redis 2>/dev/null || echo "")
  [ "$status" = "healthy" ] && break
  sleep 2
done
if [ "$status" != "healthy" ]; then
  echo "ERROR: redis did not become healthy"; $compose logs redis | tail -30; exit 1
fi

echo ":: Running redis service tests against redis ::"
set -a; source "$intdir/env/redis.env"; set +a
export PYTHONPATH=./tests/apps
poetry run pytest --color=yes --log-level=WARNING -W ignore::DeprecationWarning \
    --ignore=tests/test_database ${extra_args:-$DEFAULT_PATHS}
