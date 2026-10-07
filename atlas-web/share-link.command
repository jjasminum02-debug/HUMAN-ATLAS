#!/bin/sh
cd "$(dirname "$0")" || exit 1
if [ ! -x .share-tools/cloudflared ]; then
  printf '%s\n' 'Cloudflare 공식 cloudflared를 .share-tools/cloudflared 에 준비해야 합니다.'
  exit 1
fi
if command -v node >/dev/null 2>&1; then
  exec node scripts/shareLocalDelivery.mjs "$@"
fi
exec '/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node' scripts/shareLocalDelivery.mjs "$@"
