"""HTTP- und Browser-Fetch.

- fetch_http(): reiner HTTP-GET (schnell, für statische Analyse).
- fetch_rendered(): Playwright-Render in Subprozess mit hartem Timeout.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

import requests

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 SEOAudit/1.0"
)

_TOOLKIT_ROOT = Path(__file__).resolve().parent.parent
_BROWSERS_PATH = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", str(_TOOLKIT_ROOT / "browsers"))
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", _BROWSERS_PATH)


@dataclass
class HttpResult:
    url: str
    final_url: str
    status: int
    elapsed_ms: float
    headers: dict
    html: str
    history: list = field(default_factory=list)
    error: str | None = None


@dataclass
class RenderResult:
    url: str
    final_url: str
    title: str
    body_text: str
    console_errors: list = field(default_factory=list)
    console_warnings: list = field(default_factory=list)
    failed_requests: list = field(default_factory=list)
    dom_ready_ms: float = 0.0
    load_ms: float = 0.0
    error: str | None = None


def _normalize_url(url: str) -> str:
    return url if url.startswith(("http://", "https://")) else "https://" + url


def fetch_http(url: str, timeout: float = 20.0) -> HttpResult:
    url = _normalize_url(url)
    history: list = []
    try:
        start = time.time()
        resp = requests.get(
            url, timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "de-DE,de;q=0.9,en;q=0.8"},
            allow_redirects=True,
        )
        elapsed = (time.time() - start) * 1000
        for h in resp.history:
            history.append((h.status_code, h.url))
        return HttpResult(url=url, final_url=str(resp.url), status=resp.status_code,
                          elapsed_ms=elapsed, headers=dict(resp.headers), html=resp.text,
                          history=history)
    except requests.RequestException as exc:  # pragma: no cover
        return HttpResult(url=url, final_url=url, status=0, elapsed_ms=0.0,
                          headers={}, html="", history=history, error=str(exc))


def render_once(url: str, timeout_ms: float = 30000.0) -> RenderResult:
    url = _normalize_url(url)
    result = RenderResult(url=url, final_url=url, title="", body_text="")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT, locale="de-DE",
                                          viewport={"width": 1366, "height": 900})
            page = context.new_page()
            console_errors, console_warnings, failed = [], [], []

            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error"
                    else console_warnings.append(m.text) if m.type == "warning" else None)
            page.on("requestfailed", lambda r: failed.append(f"{r.method} {r.url} -> {r.failure}"))
            page.on("response", lambda r: failed.append(f"{r.request.method} {r.url} -> HTTP {r.status}")
                    if r.status >= 400 and not r.url.startswith("data:") else None)

            start = time.time()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            dom_ready = (time.time() - start) * 1000
            page.wait_for_load_state("networkidle", timeout=15000)
            load_ms = (time.time() - start) * 1000

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            page.evaluate("window.scrollTo(0, 0)")

            result.final_url = page.url
            result.title = page.title()
            result.body_text = page.inner_text("body") or ""
            result.console_errors = console_errors
            result.console_warnings = console_warnings
            result.failed_requests = failed
            result.dom_ready_ms = dom_ready
            result.load_ms = load_ms
            browser.close()
    except Exception as exc:  # noqa: BLE001
        result.error = str(exc)
    return result


def _run_worker(args: list, timeout: float = 50.0) -> str | None:
    worker = Path(__file__).resolve().parent / "_pw_worker.py"
    try:
        proc = subprocess.run([sys.executable, str(worker), *args],
                              capture_output=True, text=True, timeout=timeout,
                              env=os.environ.copy())
        return proc.stdout
    except (subprocess.TimeoutExpired, OSError):
        return None


def fetch_rendered(url: str, timeout_ms: float = 30000.0) -> RenderResult:
    url = _normalize_url(url)
    out = _run_worker(["render", url], timeout=30.0)
    if out is None:
        return RenderResult(url=url, final_url=url, title="", body_text="",
                            error="Render-Timeout (Chromium-Start hing; Sandbox-Flakiness, bitte erneut versuchen)")
    try:
        return RenderResult(**json.loads(out))
    except (json.JSONDecodeError, TypeError):
        return RenderResult(url=url, final_url=url, title="", body_text="", error=f"Render-Fehler: {out[:200]}")


def robots_txt(domain: str, timeout: float = 10.0) -> str:
    try:
        r = requests.get(f"{domain}/robots.txt", timeout=timeout, headers={"User-Agent": USER_AGENT})
        return r.text if r.status_code == 200 else ""
    except requests.RequestException:
        return ""


def sitemap_urls(domain: str, robots_content: str, timeout: float = 10.0) -> list:
    urls = []
    for line in robots_content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("sitemap:"):
            urls.append(stripped.split(":", 1)[1].strip())
    urls.append(f"{domain}/sitemap.xml")
    return urls


def domain_of(url: str) -> str:
    parsed = urllib.parse.urlparse(_normalize_url(url))
    return f"{parsed.scheme}://{parsed.netloc}"


def check_environment() -> str:
    out = _run_worker(["check"], timeout=30.0)
    if out is None:
        return "Playwright-Chromium: TIMEOUT (bitte erneut versuchen oder ./setup.sh)"
    try:
        return json.loads(out).get("msg", "Playwright-Chromium: unbekannte Antwort")
    except json.JSONDecodeError:
        return f"Playwright-Chromium: FEHLT ({out[:200]})"
