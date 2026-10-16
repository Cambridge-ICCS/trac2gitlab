#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="trac2gitlab-gitlab-container"

docker build \
  --file "$SCRIPT_DIR/GitLabNoVolume" \
  --tag "$IMAGE" \
  "$SCRIPT_DIR"
