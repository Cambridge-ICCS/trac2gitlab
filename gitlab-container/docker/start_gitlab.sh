#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="trac2gitlab-gitlab-container"

docker run -d \
  --name gitlab-test \
  --hostname gitlab.example.com \
  -p 443:443 \
  -p 80:80 \
  -p 2222:22 \
  "$IMAGE"
