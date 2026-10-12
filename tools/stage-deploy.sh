#!/bin/bash
# Publishes the committed state of the `stage` branch to stage.andrewkuznetsov.com
# (repo Kuznetsov-photo-art/portfolio-stage, GitHub Pages from its main).
# The copy is hidden from search engines and carries a small STAGE badge. Production (main) is never touched.
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel)
REMOTE=git@github.com:Kuznetsov-photo-art/portfolio-stage.git
DOMAIN=stage.andrewkuznetsov.com
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
git -C "$ROOT" archive stage | tar -x -C "$TMP"
cd "$TMP"
mkdir -p assets/og && cp tools/og-stage.jpg assets/og/og-stage.jpg   # link preview with a TEST stamp (tools/make_og_stage.py)
rm -rf history lab tools STATUS.md
echo "$DOMAIN" > CNAME
printf 'User-agent: *\nDisallow: /\n' > robots.txt
BADGE='<div aria-hidden="true" style="position:fixed;left:8px;bottom:calc(8px + env(safe-area-inset-bottom,0px));z-index:9999;font:600 10px/1 ui-monospace,Menlo,monospace;letter-spacing:.1em;background:#E5484D;color:#fff;padding:4px 6px;border-radius:4px;pointer-events:none">STAGE</div>'
find . -name '*.html' -print0 | while IFS= read -r -d '' f; do
  perl -0pi -e 's{<head>}{<head>\n<meta name="robots" content="noindex,nofollow">}; s{</body>}{'"$BADGE"'\n</body>}' "$f"
  # link previews point at the stage: TEST card, stage URLs, «TEST ·» in the title
  perl -pi -e 's{(<meta (?:property="og:image"|name="twitter:image") content=")https://andrewkuznetsov\.com/assets/og/[^"]+}{${1}https://'"$DOMAIN"'/assets/og/og-stage.jpg?v=1}g; s{(<meta property="og:url" content="|<link rel="canonical" href=")https://andrewkuznetsov\.com}{${1}https://'"$DOMAIN"'}g; s{(<meta property="og:title" content=")}{${1}TEST · }g; s{<meta name="robots" content="index,follow">\n?}{}g' "$f"
done
REV=$(git -C "$ROOT" rev-parse --short stage)
git init -q -b main
git add -A
git -c user.name="Kuznetsov-photo-art" -c user.email="Kuznetsov-photo-art@users.noreply.github.com" commit -q -m "Stage build of $REV"
for i in 1 2 3; do git push -q -f "$REMOTE" main && break; sleep 3; done
echo "stage: $REV → https://$DOMAIN"
