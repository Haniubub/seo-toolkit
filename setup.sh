#!/usr/bin/env bash
# Einrichtung des SEO-Toolkits: baut ein eigenständiges, selbsttragendes Setup auf.
# 1) Python-Abhängigkeiten in workspace-lokal pylibs/ (pip --target) -- KEIN globales Setup.
# 2) Playwright-Chromium in workspace-lokal browsers/.
# 3) Smoke-Test über ./seo doctor.
#
# Nach dem Lauf ist das Toolkit aus einem frischen clone/download voll lauffähig.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
export PLAYWRIGHT_BROWSERS_PATH="$HERE/browsers"
PY="${PYTHON:-python3}"
REQ="$HERE/requirements.txt"

echo "==> 1/3 Python-Abhängigkeiten nach pylibs/ (workspace-lokal)"
echo "    Ziel: $HERE/pylibs  |  Quelle: $REQ"
if [ ! -f "$REQ" ]; then
  echo "FEHLER: $REQ nicht gefunden." >&2
  exit 1
fi
# --upgrade, damit vorhandene, aber veraltete Pakete auf die gepinnten Versionen gehoben werden.
"$PY" -m pip install --quiet --upgrade --target "$HERE/pylibs" -r "$REQ"

echo "==> 2/3 Playwright-Chromium installieren (in $HERE/browsers)"
"$PY" -m playwright install chromium

echo "==> 3/3 Smoke-Test"
"$PY" -c "import sys; sys.path.insert(0,'$HERE'); from lib.fetch import check_environment; print(check_environment())"

echo ""
echo "Fertig. Aufruf über: ./seo doctor  |  ./seo audit <url>"
