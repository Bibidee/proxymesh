#!/usr/bin/env bash
set -euo pipefail
WANTED="0.39.1"
if ! command -v genlayer >/dev/null 2>&1; then
  echo "genlayer CLI is not installed. Install exact stable version with: npm install -g genlayer@${WANTED}"
  exit 2
fi
ACTUAL="$(genlayer --version 2>&1 || true)"
echo "$ACTUAL"
if [[ "$ACTUAL" != *"$WANTED"* ]]; then
  echo "ERROR: ProxyMesh requires GenLayer CLI ${WANTED}; do not use 0.4.0 or the v0.40 RC line." >&2
  exit 3
fi

genlayer network set studionet
genlayer network info
