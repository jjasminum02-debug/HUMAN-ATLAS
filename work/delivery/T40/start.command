#!/bin/sh
cd "$(dirname "$0")/../../../atlas-web" || exit 1
T40_NODE_BIN="$(command -v node 2>/dev/null || true)"
if [ -z "$T40_NODE_BIN" ]; then
  T40_NODE_BIN="/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
fi
exec "$T40_NODE_BIN" scripts/runLocalDelivery.mjs "$@"
