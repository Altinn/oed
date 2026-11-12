#!/usr/bin/env bash
# Regenerate the .drawio files in docs/ and preview them locally.
#
# Run from the repository root:  bash docs/tools/render.sh
#
# The generators overwrite the .drawio files, so hand edits made in draw.io are lost
# unless they are also made in gen.py / gen_more.py. Commit only the .drawio files;
# the "Export draw.io diagrams" workflow builds the light/dark SVGs on push.
#
# The preview uses the same export image and flags as the workflow and writes to
# a temporary folder (requires Docker).
set -euo pipefail
cd "$(dirname "$0")/../.."
python docs/tools/gen.py docs/oed.drawio
python docs/tools/gen_more.py docs

out="$(mktemp -d)"
cp docs/*.drawio "$out/"
mount="$(cd "$out" && (pwd -W 2>/dev/null || pwd))"  # Windows path under Git Bash
for theme in light dark; do
  MSYS_NO_PATHCONV=1 docker run --rm -v "$mount:/data" -w /data rlespinasse/drawio-export:v4.56.0 \
    --format svg --output . --remove-page-suffix --border 100 --embed-svg-fonts false --svg-theme "$theme" . >/dev/null
  for f in "$out"/*.svg; do
    case "$f" in *-light.svg|*-dark.svg) continue;; esac
    mv "$f" "${f%.svg}-$theme.svg"
  done
done
{
  echo '<!doctype html><html><head><meta charset="utf-8"><title>OED diagrams</title><style>body{margin:0;font-family:sans-serif}section{padding:12px 24px}h2{font-size:15px}.l{background:#fff;color:#1f2328}.d{background:#0d1117;color:#e6edf3}img{max-width:100%;display:block;margin:0 auto 24px}</style></head><body>'
  for f in "$out"/*-light.svg; do
    b=$(basename "${f%-light.svg}")
    echo "<section class=\"l\"><h2>$b (light)</h2><img src=\"$b-light.svg\"></section>"
    echo "<section class=\"d\"><h2>$b (dark)</h2><img src=\"$b-dark.svg\"></section>"
  done
  echo '</body></html>'
} > "$out/preview.html"
echo "Preview: $out/preview.html"
