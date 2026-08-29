#!/usr/bin/env bash
# Einrichtung des SEO-Toolkits: nutzt das vorhandene Python 3 und installiert
# nur Playwright-Chromium workspace-lokal (browsers/). Kein globales System-Setup.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
export PLAYWRIGHT_BROWSERS_PATH="$HERE/browsers"
PY="${PYTHON:-python3}"
echo "==> 1/3 Python-Abhängigkeiten prüfen"
"$PY" - <<'PYEOF'
import importlib, sys
missing = []
for mod in ("requests", "bs4", "lxml", "playwright"):
    try:
        importlib.import_module(mod)
    except ImportError as exc:
        missing.append(f"{mod} ({exc})")
if missing:
    print("FEHLENDE Pakete:", ", ".join(missing))
    print("Bitte installieren: python3 -m pip install -r requirements.txt")
    sys.exit(1)
print("Abhängigkeiten: OK")
PYEOF
echo "==> 2/3 Playwright-Chromium installieren (in $HERE/browsers)"
"$PY" -m playwright install chromium
echo "==> 3/3 Prüfen"
"$PY" -c "import sys; sys.path.insert(0,'.'); from lib.fetch import check_environment; print(check_environment())"
echo ""
echo "Fertig. Aufruf über: ./seo doctor  |  ./seo audit <url>"
