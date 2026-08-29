#!/usr/bin/env python3
"""SEO-Orchestrator — CLI-Einstieg (voller Befehlsfläche, portiert von claude-seo).

Messung (Python) und Urteil (LLM-Sub-Skills/Agents) sind getrennt:
- Alle ./seo <cmd>-Befehle hier messen (eigene Specialists + portierte Skripte).
- Urteilsintensive Befehle werden vom Agent über die Sub-Skills in skills/ ausgeführt.

Verwendung:
  ./seo doctor  |  ./seo audit <url>  |  technical|page|schema|local|visual|sitemap|content|hreflang|backlinks
  ./seo cluster <keyword>  |  content-brief <topic> [keyword]
  ./seo drift baseline|compare|history <url>  |  google <sub> [args]  |  run <script.py> [args]  |  list
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
SKILLS_DIR = ROOT / "skills"
PYLIBS = ROOT / "pylibs"
BROWSERS = ROOT / "browsers"
DATA_DIR = ROOT / "data"

sys.path.insert(0, str(ROOT))

from lib import (  # noqa: E402
    checks_geo, checks_page, checks_schema, checks_technical, checks_visual,
    cluster, drift,
)
from lib.fetch import check_environment, fetch_http, fetch_rendered  # noqa: E402
from lib.report import AuditResult, render_json, render_markdown  # noqa: E402

SECRET_PATTERNS = (
    (re.compile(r"(?i)(https?://[^\s:/]+:)[^@\s]+@"), r"\1<redacted>@"),
    (re.compile(r"(?i)(https?://[^\s?]+\?)[^\s]+"), r"\1<redacted>"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "<redacted-email>"),
    (re.compile(r"(?i)(token|password|secret|api[_-]?key)([=:\s]+)[^\s]+"), r"\1\2<redacted>"),
)


def _redact(text: str) -> str:
    for pat, repl in SECRET_PATTERNS:
        text = pat.sub(repl, text)
    return text


def _script_env() -> dict:
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = env.get("PLAYWRIGHT_BROWSERS_PATH", str(BROWSERS))
    env["PYTHONUNBUFFERED"] = "1"
    pp = env.get("PYTHONPATH", "")
    base = os.pathsep.join([str(PYLIBS), str(SCRIPTS_DIR)])
    env["PYTHONPATH"] = base + (os.pathsep + pp if pp else "")
    return env


def _run_script(name: str, *args: str, timeout: float = 45.0, input_text: str | None = None) -> int:
    if not name.endswith(".py"):
        name += ".py"
    script = (SCRIPTS_DIR / name).resolve()
    if not str(script).startswith(str(SCRIPTS_DIR.resolve())) or not script.is_file():
        print(f"Unbekanntes Skript: {name}")
        return 2
    try:
        proc = subprocess.run([sys.executable, str(script), *args], env=_script_env(),
                              timeout=timeout, input=input_text, text=True, capture_output=True)
        if proc.stdout:
            sys.stdout.write(_redact(proc.stdout))
            if not proc.stdout.endswith("\n"):
                sys.stdout.write("\n")
        if proc.stderr:
            sys.stderr.write(_redact(proc.stderr))
        return proc.returncode
    except subprocess.TimeoutExpired:
        print(f"Skript {name} nach {timeout:.0f}s abgebrochen (Sandbox-Netz/DNS-Flakiness — bitte erneut versuchen).")
        return 124


def _save(result: AuditResult) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = result.timestamp.replace(":", "").replace("-", "").replace("+", "")[:14]
    out = DATA_DIR / f"audit-{stamp}.json"
    out.write_text(render_json(result), encoding="utf-8")
    return out


def _fetch_both(url: str):
    http = fetch_http(url)
    render = None
    try:
        render = fetch_rendered(url)
    except Exception:  # noqa: BLE001
        render = None
    return http, render


def _specialists() -> dict:
    return {"technical": checks_technical.run, "page": checks_page.run,
            "schema": checks_schema.run, "local": checks_geo.run, "visual": checks_visual.run}


def _run_parallel(http, render, names: list) -> dict:
    specs = _specialists()
    results = {}

    def work(name):
        fn = specs[name]
        if name == "visual":
            return name, fn(http, render) if render else None
        if name in ("page", "local"):
            return name, fn(http, render.body_text if render else "")
        return name, fn(http)

    with ThreadPoolExecutor(max_workers=len(names)) as pool:
        for fut in as_completed({pool.submit(work, n): n for n in names}):
            name, cat = fut.result()
            if cat is not None:
                results[name] = cat
    return results


def detect_business_type(http) -> str:
    html = (http.html or "").lower()
    url = (http.final_url or "").lower()
    signals = {
        "saas": ["pricing", "/features", "/integrations", "/docs", "free trial", "sign up"],
        "ecommerce": ["/products", "/collections", "/cart", "add to cart", "product", "shop"],
        "publisher": ["/blog", "/articles", "/topics", "author", "published"],
        "agency": ["/case-studies", "/portfolio", "/industries", "our work", "client"],
        "local-service": ["phone", "tel:", "address", "service area", "serving ", "google.com/maps", "öffnungszeit"],
    }
    for biz, keys in signals.items():
        if any(k in html or k in url for k in keys):
            return biz
    return "other"


def _agent_cmd(skill_path: str, note: str) -> int:
    print(f"[Agent-Befehl] {note}")
    print(f"Sub-Skill: {skill_path}")
    print("Erfordert LLM-Urteil — als Agent ausführen (SKILL.md laden, ggf. web_search/subagent).")
    return 0


AGENT_COMMANDS = {
    "geo": ("skills/seo-geo/SKILL.md", "GEO / AI Overviews (ChatGPT, Perplexity, AI-Overview)."),
    "plan": ("skills/seo-plan/SKILL.md", "Strategische SEO-Planung je Branche."),
    "programmatic": ("skills/seo-programmatic/SKILL.md", "Programmatic-SEO-Analyse."),
    "competitor-pages": ("skills/seo-competitor-pages/SKILL.md", "Vergleichsseiten-Generierung."),
    "maps": ("skills/seo-maps/SKILL.md", "Maps-Intelligence (Geo-Grid, GBP-Audit, Reviews)."),
    "sxo": ("skills/seo-sxo/SKILL.md", "Search Experience Optimization (Personas, User Stories)."),
    "flow": ("skills/seo-flow/SKILL.md", "FLOW-Framework (Find/Leverage/Optimize/Win/Local)."),
    "images": ("skills/seo-images/SKILL.md", "Bilder-SEO (Audit + Optimierung)."),
}
EXTENSION_COMMANDS = {
    "image-gen": ("extensions/banana/skills/seo-image-gen/SKILL.md", "KI-Bildgenerierung (Banana/Gemini)."),
    "dataforseo": ("extensions/dataforseo/skills/seo-dataforseo/SKILL.md", "Live-SEO-Daten via DataForSEO."),
    "firecrawl": ("extensions/firecrawl/skills/seo-firecrawl/SKILL.md", "Full-Site-Crawling via Firecrawl."),
    "ahrefs": ("extensions/ahrefs/skills/seo-ahrefs/SKILL.md", "Backlink-/Wettbewerbsdaten via Ahrefs."),
    "bing": ("extensions/bing-webmaster/skills/seo-bing/SKILL.md", "Bing Webmaster Tools."),
    "profound": ("extensions/profound/skills/seo-profound/SKILL.md", "profound-Daten."),
    "seranking": ("extensions/seranking/skills/seo-seranking/SKILL.md", "SE Ranking-Daten."),
    "unlighthouse": ("extensions/unlighthouse/skills/seo-unlighthouse/SKILL.md", "Lighthouse-Site-Scans."),
}


def cmd_doctor() -> int:
    print("SEO-Toolkit Status:")
    try:
        import requests as r
        print(f"- Python/Requests: OK (requests {r.__version__})")
    except Exception as exc:  # noqa: BLE001
        print(f"- Requests: FEHLT ({exc})")
    print(f"- {check_environment()}")
    try:
        import trafilatura, openpyxl  # noqa: F401
        print("- Content-Extraktion (trafilatura) + Excel (openpyxl): OK")
    except Exception as exc:  # noqa: BLE001
        print(f"- Zusatz-Deps: FEHLT ({exc})")
    try:
        fetch_http("https://example.com", timeout=8)
        print("- Netzwerk: OK (example.com erreichbar)")
    except Exception as exc:  # noqa: BLE001
        print(f"- Netzwerk: FEHLER ({exc})")
    print(f"- Portierte Skripte: {len(list(SCRIPTS_DIR.glob('*.py')))} · Sub-Skills: {len(list(SKILLS_DIR.iterdir()))}")
    return 0


def cmd_audit(url: str, only: str | None = None) -> int:
    names = [only] if only else list(_specialists().keys())
    http = fetch_http(url)
    render = None
    if only is None or only == "visual":
        try:
            render = fetch_rendered(url)
        except Exception:  # noqa: BLE001
            render = None
    if only is None:
        print(f"[Branche erkannt: {detect_business_type(http)}]\n")
    result = AuditResult(url=url)
    for name, cat in _run_parallel(http, render, names).items():
        result.categories[name] = cat
    result.metrics = {"http_status": http.status, "final_url": http.final_url,
                      "redirect_hops": len(http.history),
                      "render_error": render.error if render else "no render",
                      "load_ms_lab": round(render.load_ms) if render else None}
    out_path = _save(result)
    print(render_markdown(result))
    print(f"\n---\n*Rohdaten gespeichert: {out_path.name}*")
    if only is None:
        print("\n## Zusatz-Messungen (portierte Skripte)")
        for label, script, args in (("Sitemap", "sitemap_discovery.py", ("--json", url)),
                                    ("HTML-Struktur", "parse_html.py", ("--url", url, "--json"))):
            print(f"\n### {label}")
            subprocess.run([sys.executable, str(SCRIPTS_DIR / script), *args], env=_script_env())
    return 0


def cmd_drift(action: str, url: str) -> int:
    if action == "history":
        return _run_script("drift_history.py", url)
    if action in ("baseline", "compare"):
        http, render = _fetch_both(url)
        result = AuditResult(url=url)
        for name, cat in _run_parallel(http, render, list(_specialists().keys())).items():
            result.categories[name] = cat
        if action == "baseline":
            print(f"Baseline gesetzt: {drift.save_baseline(result)}")
            return 0
        print(drift.compare(url, result))
        return 0
    print("Aufruf: ./seo drift baseline|compare|history <url>")
    return 1


def cmd_list() -> int:
    print("Portierte Skripte (scripts/):")
    for p in sorted(SCRIPTS_DIR.glob("*.py")):
        print(f"  {p.name}")
    print("\nSub-Skills (skills/):")
    for p in sorted(SKILLS_DIR.iterdir()):
        if p.is_dir():
            print(f"  {p.name}")
    print("\nExtensions (extensions/):")
    for p in sorted((ROOT / "extensions").iterdir()):
        if p.is_dir():
            print(f"  {p.name}")
    return 0


def main(argv: list) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]

    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "list":
        return cmd_list()
    if cmd == "run":
        return _run_script(argv[1], *argv[2:]) if len(argv) > 1 else (print("Aufruf: ./seo run <script.py> [args]") or 1)
    if cmd == "audit":
        return cmd_audit(argv[1]) if len(argv) > 1 else (print("Aufruf: ./seo audit <url>") or 1)
    if cmd in ("technical", "page", "schema", "local", "visual"):
        return cmd_audit(argv[1], only=cmd) if len(argv) > 1 else (print(f"Aufruf: ./seo {cmd} <url>") or 1)
    if cmd == "sitemap":
        return _run_script("sitemap_discovery.py", "--json", argv[1]) if len(argv) > 1 else (print("Aufruf: ./seo sitemap <url>") or 1)
    if cmd == "content":
        if len(argv) < 2:
            print("Aufruf: ./seo content <url|datei>")
            return 1
        src = argv[1]
        if src.startswith(("http://", "https://")):
            http = fetch_http(src)
            if http.error:
                print(f"Fetch-Fehler: {http.error}")
                return 1
            from lib.htmlutil import soup as _soup
            text = _soup(http.html).get_text(" ", strip=True)
            return _run_script("content_quality.py", "--json", "-", input_text=text)
        return _run_script("content_quality.py", "--json", src)
    if cmd == "hreflang":
        return _run_script("parse_html.py", "--url", argv[1], "--json") if len(argv) > 1 else (print("Aufruf: ./seo hreflang <url>") or 1)
    if cmd == "backlinks":
        print("[Hinweis] Freie Backlink-Quellen (Moz, Bing, Common Crawl). Premium: DataForSEO.")
        _run_script("backlinks_auth.py", "--check")
        return _run_script("verify_backlinks.py", argv[1]) if len(argv) > 1 else (print("Aufruf: ./seo backlinks <url>") or 1)
    if cmd == "cluster":
        return (print(cluster.cluster_report(argv[1], [])) or 0) if len(argv) > 1 else (print("Aufruf: ./seo cluster <keyword>") or 1)
    if cmd == "content-brief":
        return (print(cluster.content_brief(argv[1], argv[2] if len(argv) > 2 else "")) or 0) if len(argv) > 1 else (print("Aufruf: ./seo content-brief <topic> [keyword]") or 1)
    if cmd == "drift":
        return cmd_drift(argv[1], argv[2]) if len(argv) > 2 else (print("Aufruf: ./seo drift baseline|compare|history <url>") or 1)
    if cmd == "google":
        mapping = {"pagespeed": "pagespeed_check.py", "crux": "crux_history.py", "gsc-query": "gsc_query.py",
                   "gsc-inspect": "gsc_inspect.py", "ga4": "ga4_report.py", "indexing": "indexing_notify.py",
                   "keyword-planner": "keyword_planner.py", "report": "google_report.py",
                   "updates": "seo_updates.py", "youtube": "youtube_search.py", "auth": "google_auth.py"}
        if len(argv) < 2:
            print("Google-APIs (benötigt Key). Sub-Befehle: pagespeed, crux, gsc-query, gsc-inspect, ga4, indexing, keyword-planner, report, updates, youtube")
            return 1
        script = mapping.get(argv[1])
        return _run_script(script, *argv[2:]) if script else (print(f"Unbekannter google-Sub-Befehl: {argv[1]}") or 1)
    if cmd == "ecommerce":
        if len(argv) < 2:
            return _agent_cmd("skills/seo-ecommerce/SKILL.md", "E-Commerce-SEO (Produkt-Schema, Marketplace).")
        print("[Messung] E-Commerce-Schema-Validierung + UCP-Check:")
        _run_script("schema_ecommerce_validate.py", argv[1])
        return _run_script("ucp_check.py", argv[1])
    if cmd in AGENT_COMMANDS:
        skill, note = AGENT_COMMANDS[cmd]
        if cmd == "images" and len(argv) > 1:
            print("[Messung] Bilder aus HTML extrahieren:")
            _run_script("parse_html.py", "--url", argv[1], "--json")
        return _agent_cmd(skill, note)
    if cmd in EXTENSION_COMMANDS:
        skill, note = EXTENSION_COMMANDS[cmd]
        return _agent_cmd(skill, note)

    print(f"Unbekannter Befehl: {cmd}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
