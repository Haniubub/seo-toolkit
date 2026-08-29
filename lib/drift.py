"""Drift-Tracking: Baseline setzen und Audits über die Zeit vergleichen."""
from __future__ import annotations

import json
import re
from pathlib import Path

from lib.report import AuditResult, SEVERITY_ORDER

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BASELINE_DIR = DATA_DIR / "baselines"


def _slug_url(url: str) -> str:
    return re.sub(r"^https?://", "", url).replace(":", "-").replace("/", "-") or "site"


def _path_for(url: str) -> Path:
    return BASELINE_DIR / f"{_slug_url(url)}.json"


def _load(url: str) -> dict | None:
    path = _path_for(url)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_baseline(result: AuditResult) -> Path:
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    path = _path_for(result.url)
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def compare(url: str, current: AuditResult) -> str:
    baseline = _load(url)
    lines = []
    if baseline is None:
        return f"Keine Baseline für {url}. Setze sie mit `./seo drift baseline {url}`."
    lines.append(f"# Drift-Vergleich – {url}")
    lines.append(f"*Baseline: {baseline['timestamp']} · Aktuell: {current.timestamp}*")
    lines.append("")
    old_score = baseline.get("overall_score", 0)
    new_score = current.overall_score()
    delta = new_score - old_score
    trend = "verbessert" if delta > 0 else ("verschlechtert" if delta < 0 else "unverändert")
    lines.append(f"## Gesamtscore: {old_score} → {new_score} ({delta:+d}, {trend})")
    lines.append("")
    lines.append("| Kategorie | Alt | Neu | Delta |")
    lines.append("|---|---|---|---|")
    old_cats = baseline.get("categories", {})
    for name, cat in current.categories.items():
        old = old_cats.get(name, {}).get("score", 0)
        d = cat.score - old
        lines.append(f"| {name} | {old} | {cat.score} | {'%+d' % d if d else '±0'} |")
    lines.append("")
    old_recs = {r["id"]: r for cat in old_cats.values() for r in cat.get("recommendations", [])}
    new_recs = {r.id: r for r in current.all_recommendations()}
    added = [r for rid, r in new_recs.items() if rid not in old_recs]
    removed = [r for rid, r in old_recs.items() if rid not in new_recs]
    changed = [(old_recs[rid]["severity"], r) for rid, r in new_recs.items()
               if rid in old_recs and old_recs[rid]["severity"] != r.severity]
    if added:
        lines.append(f"## Neu aufgetaucht ({len(added)})")
        for r in sorted(added, key=lambda x: -SEVERITY_ORDER[x.severity]):
            lines.append(f"- [{r.severity}] {r.title}")
    if removed:
        lines.append(f"\n## Behoben ({len(removed)})")
        for r in removed:
            lines.append(f"- ~~{r['title']}~~ (war {r['severity']})")
    if changed:
        lines.append("\n## Schweregrad geändert")
        for old_sev, r in changed:
            lines.append(f"- {r.title}: {old_sev} → {r.severity}")
    if not added and not removed and not changed:
        lines.append("Keine Veränderung bei den Empfehlungen seit der Baseline.")
    return "\n".join(lines)
