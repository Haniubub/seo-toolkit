#!/usr/bin/env python3
"""Playwright-Worker.

Wird von lib/fetch.py per subprocess mit hartem Timeout aufgerufen, damit ein
hängender Chromium-Start (gelegentlich unter der Sandbox) den Orchestrator
nicht blockiert. Gibt JSON auf stdout aus.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / "browsers")),
)


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
            print(json.dumps({"ok": True, "msg": "Playwright-Chromium: OK"}))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"ok": False, "msg": f"Playwright-Chromium: FEHLT ({exc}). Bitte ./setup.sh ausführen."}))
    elif cmd == "render":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        from lib.fetch import render_once

        r = render_once(url)
        print(json.dumps(r.__dict__, ensure_ascii=False))
    else:
        print(json.dumps({"ok": False, "msg": f"unbekannter Worker-Befehl: {cmd}"}))


if __name__ == "__main__":
    main()
