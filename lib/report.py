"""Datenmodell, gewichteter Score und Berichtserzeugung.

Jede Empfehlung trägt vier Felder: Beobachtung → Abhängigkeit → Misserfolgssignal → Frühindikator.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

SEVERITY_ORDER = {"critical": 4, "warning": 3, "info": 2, "pass": 1}
SEVERITY_LABEL = {"critical": "Kritisch", "warning": "Warnung", "info": "Hinweis", "pass": "OK"}

CATEGORY_WEIGHTS = {
    "technical": 22, "content": 23, "page": 20, "schema": 10,
    "performance": 10, "visual": 10, "ai": 10, "geo": 10, "local": 10, "images": 5,
}


@dataclass
class Finding:
    category: str
    severity: str
    title: str
    observation: str
    detail: str = ""


@dataclass
class Recommendation:
    id: str
    category: str
    severity: str
    title: str
    observation: str
    dependency: str
    failure_signal: str
    early_indicator: str
    related: list = field(default_factory=list)


@dataclass
class CategoryResult:
    category: str
    findings: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    score: int = 0

    def to_dict(self):
        return {"category": self.category, "score": self.score,
                "findings": [asdict(f) for f in self.findings],
                "recommendations": [asdict(r) for r in self.recommendations]}


@dataclass
class AuditResult:
    url: str
    timestamp: str = ""
    categories: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def category(self, name: str) -> CategoryResult:
        return self.categories.setdefault(name, CategoryResult(category=name))

    def all_findings(self) -> list:
        return [f for c in self.categories.values() for f in c.findings]

    def all_recommendations(self) -> list:
        return [r for c in self.categories.values() for r in c.recommendations]

    def overall_score(self) -> int:
        total_w = 0
        weighted = 0
        for name, c in self.categories.items():
            if c.score is None:
                continue
            w = CATEGORY_WEIGHTS.get(name, 10)
            total_w += w
            weighted += w * c.score
        return round(weighted / total_w) if total_w else 0

    def to_dict(self) -> dict:
        return {"url": self.url, "timestamp": self.timestamp,
                "overall_score": self.overall_score(), "metrics": self.metrics,
                "categories": {k: v.to_dict() for k, v in self.categories.items()}}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9äöüß]+", "-", text.lower()).strip("-")


def make_recommendation(category, severity, title, observation, dependency,
                        failure_signal, early_indicator, related=None):
    return Recommendation(id=f"{_slug(category)}-{_slug(title)[:40]}", category=category,
                          severity=severity, title=title, observation=observation,
                          dependency=dependency, failure_signal=failure_signal,
                          early_indicator=early_indicator, related=related or [])


def score_category(category: CategoryResult) -> int:
    weights = {"critical": 15, "warning": 5, "info": 1, "pass": 0}
    penalty = sum(weights.get(getattr(f, "severity", "info"), 1)
                  for f in category.findings + list(category.recommendations))
    return max(0, 100 - penalty)


def ordered_recommendations(result: AuditResult) -> list:
    recs = result.all_recommendations()
    ids = {r.id for r in recs}
    by_id = {r.id: r for r in recs}
    ordered = sorted(recs, key=lambda r: -SEVERITY_ORDER[r.severity])

    def deps_ok(seq):
        pos = {r.id: i for i, r in enumerate(seq)}
        return all(pos.get(dep, 0) <= pos[r.id] for r in seq for dep in r.related if dep in ids)

    for _ in range(50):
        if deps_ok(ordered):
            break
        for i, r in enumerate(ordered):
            for dep in r.related:
                if dep in by_id:
                    dep_idx = next((j for j, x in enumerate(ordered) if x.id == dep), -1)
                    if dep_idx > i:
                        ordered.pop(dep_idx)
                        ordered.insert(i, by_id[dep])
                        break
    return ordered


def render_markdown(result: AuditResult) -> str:
    lines = [f"# SEO-Befund – {result.url}",
             f"*Zeitpunkt: {result.timestamp} · Gesamtscore: {result.overall_score()}/100*", ""]
    lines.append("## Überblick nach Kategorie")
    lines.append("")
    lines.append("| Kategorie | Score | Kritisch | Warnung | Hinweis |")
    lines.append("|---|---|---|---|---|")
    for cat in result.categories.values():
        items = cat.findings + list(cat.recommendations)
        crit = sum(1 for f in items if f.severity == "critical")
        warn = sum(1 for f in items if f.severity == "warning")
        info = sum(1 for f in items if f.severity == "info")
        lines.append(f"| {cat.category} | {cat.score} | {crit} | {warn} | {info} |")
    lines.append("")
    findings = result.all_findings()
    if findings:
        lines.append("## Befunde")
        for f in sorted(findings, key=lambda x: -SEVERITY_ORDER[x.severity]):
            lines.append(f"- **[{SEVERITY_LABEL.get(f.severity, f.severity)}] {f.title}** ({f.category})")
            lines.append(f"  - Beobachtung: {f.observation}")
            if f.detail:
                lines.append(f"  - Detail: {f.detail}")
    lines.append("")
    recs = ordered_recommendations(result)
    if recs:
        lines.append(f"## Priorisierter Aktionsplan ({len(recs)} Empfehlungen)")
        lines.append("")
        for i, r in enumerate(recs, 1):
            lines.append(f"### {i}. [{SEVERITY_LABEL.get(r.severity, r.severity)}] {r.title}")
            lines.append(f"- **Beobachtung:** {r.observation}")
            lines.append(f"- **Abhängigkeit:** {r.dependency}")
            lines.append(f"- **Misserfolgssignal:** {r.failure_signal}")
            lines.append(f"- **Frühindikator:** {r.early_indicator}")
            if r.related:
                lines.append(f"- **Verwandt:** {', '.join(r.related)}")
            lines.append("")
    if result.metrics:
        lines.append("## Kennzahlen")
        lines.append("```json")
        lines.append(json.dumps(result.metrics, ensure_ascii=False, indent=2))
        lines.append("```")
    return "\n".join(lines)


def render_json(result: AuditResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
