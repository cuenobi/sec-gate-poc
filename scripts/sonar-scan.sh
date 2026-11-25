#!/bin/sh
# Usage: scripts/sonar-scan.sh <service dir>. Needs SONAR_HOST_URL and SONAR_TOKEN (read from .env locally).
set -eu
dir=$1

if [ -f .env ]; then
    set -a
    . ./.env
    set +a
    export SONAR_HOST_URL="${SONAR_HOST_URL:-http://sonarqube:9000}"
    SONAR_NETWORK="${SONAR_NETWORK:-sec-gate-poc_default}"
fi
export SONAR_HOST_URL="${SONAR_HOST_URL:-https://sonarqube.khaojai.it}"

set --
if [ -n "${CHANGE_ID:-}" ]; then
    set -- -Dsonar.pullrequest.key="$CHANGE_ID" \
        -Dsonar.pullrequest.branch="$CHANGE_BRANCH" -Dsonar.pullrequest.base="$CHANGE_TARGET"
elif [ -n "${CI_BRANCH:-}" ]; then
    set -- -Dsonar.branch.name="$CI_BRANCH"
fi

# The image's default work dir /tmp/.scannerwork is root-owned; the scanner runs as the caller's uid.
docker run --rm ${SONAR_NETWORK:+--network "$SONAR_NETWORK"} \
    --user "$(id -u):$(id -g)" -e HOME=/tmp -e SONAR_USER_HOME=/tmp/sonar \
    -e SCANNER_WORKDIR_PATH=/tmp/scannerwork -e SONAR_HOST_URL -e SONAR_TOKEN \
    -v "$PWD:$PWD" -w "$PWD/$dir" \
    sonarsource/sonar-scanner-cli:12.5.0.4351_8.5.0 \
    -Dsonar.projectBaseDir="$PWD/$dir" -Dsonar.qualitygate.wait=true "$@"
