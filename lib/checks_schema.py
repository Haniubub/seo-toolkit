"""Strukturierte Daten (Schema.org) prüfen: JSON-LD, LocalBusiness-Relevanz."""
from __future__ import annotations

import json

from lib.fetch import HttpResult
from lib.htmlutil import soup
from lib.report import CategoryResult, Finding, make_recommendation, score_category

LOCAL_TYPES = {
    "LocalBusiness", "Restaurant", "AutoRepair", "AutoBodyShop", "AutomotiveBusiness",
    "ProfessionalService", "Service", "Organization", "Store", "MedicalBusiness",
    "LegalService", "HomeAndConstructionBusiness", "LodgingBusiness", "FoodEstablishment",
}
LOCAL_REQUIRED = ["name", "address", "telephone"]


def _types_of(data) -> set:
    found = set()

    def walk(obj):
        if isinstance(obj, dict):
            t = obj.get("@type")
            if isinstance(t, str):
                found.add(t)
            elif isinstance(t, list):
                found.update(str(x) for x in t)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    return found


def run(http: HttpResult) -> CategoryResult:
    cat = CategoryResult(category="schema")
    if http.error:
        cat.score = 0
        return cat
    s = soup(http.html)
    scripts = s.find_all("script", attrs={"type": "application/ld+json"})
    blocks, parse_errors = [], []
    for sc in scripts:
        raw = sc.string or sc.get_text() or ""
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            parse_errors.append(str(exc))

    if not scripts:
        cat.recommendations.append(make_recommendation("schema", "critical", "Keine strukturierten Daten (JSON-LD)",
            "Kein <script type='application/ld+json'> gefunden.", "Nach Content- und On-Page-Optimierung; vor Geo-Optimierung.",
            "Keine Rich Results im SERP.", "Rich-Results-Test meldet gültige strukturierte Daten."))
        cat.score = score_category(cat)
        return cat

    if parse_errors:
        cat.recommendations.append(make_recommendation("schema", "critical", "JSON-LD nicht parsebar",
            f"{len(parse_errors)} Block(s) mit Syntaxfehler: {parse_errors[0][:80]}",
            "Zuerst beheben — kaputtes JSON-LD wird ignoriert.", "Rich-Results-Test zeigt Fehler.",
            "Alle JSON-LD-Blöcke parsen fehlerfrei."))

    all_types = set()
    for b in blocks:
        all_types |= _types_of(b)
    cat.findings.append(Finding("schema", "info", "Gefundene Schema-Typen",
                                "Typen: " + (", ".join(sorted(all_types)) or "—"),
                                f"{len(blocks)} JSON-LD-Block(block)."))

    local = all_types & LOCAL_TYPES
    if local:
        block = blocks[0]
        flat = json.dumps(block, ensure_ascii=False)
        missing = [k for k in LOCAL_REQUIRED if k not in flat]
        if missing:
            cat.recommendations.append(make_recommendation("schema", "warning", "LocalBusiness-Daten unvollständig",
                f"Typ {sorted(local)[0]} ohne: {', '.join(missing)}.", "Mit Geo/NAP-Daten abgleichen.",
                "Kein lokales Rich Result.", "name, address und telephone sind im JSON-LD enthalten."))
        else:
            cat.findings.append(Finding("schema", "pass", "NAP im Schema vollständig",
                                        "name, address, telephone vorhanden.", ""))
    else:
        cat.recommendations.append(make_recommendation("schema", "info", "Kein LocalBusiness-Schema",
            "Keine lokalen Typen (LocalBusiness/Restaurant/…) gefunden.",
            "Für lokale Sichtbarkeit nach Content einbauen.",
            "Lokale Suchanfragen lösen kein lokales Rich Result aus.",
            "Lokale Typen + NAP sind im JSON-LD vorhanden."))

    microdata = s.find_all(attrs={"itemtype": True})
    if microdata:
        cat.findings.append(Finding("schema", "info", "Microdata vorhanden", f"{len(microdata)} Element(e) mit itemtype.", ""))

    cat.score = score_category(cat)
    return cat
