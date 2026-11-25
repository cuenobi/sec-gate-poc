#!/bin/sh
# Usage: scripts/verify.sh <service dir>. Runs khaojai-ci's Python Verify locally.
set -eu
dir=$1
lib=$(cd "${KHAOJAI_CI:-../jenkins-library}/resources/com/khaojai/ci" && pwd)
docker run --rm -v "$PWD:$PWD" -v "$lib:/ci:ro" -w "$PWD/$dir" -e CI=true \
    --entrypoint sh ghcr.io/astral-sh/uv:python3.13-bookworm-slim -eu /ci/verify-python.sh
