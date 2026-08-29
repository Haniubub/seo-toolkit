"""Keyword-Clustering und Content-Brief (heuristisch, ohne Fremdindex)."""
from __future__ import annotations

import re
from collections import Counter

from lib.htmlutil import words, STOPWORDS

INTENT_MARKERS = {
    "transactional": ["kaufen", "preis", "kosten", "anfrage", "termin", "buchen", "bestellen", "angebot",
                      "buy", "price", "cost", "quote", "book", "hire"],
    "informational": ["was ist", "wie", "warum", "anleitung", "ratgeber", "tipps", "checkliste",
                      "what is", "how to", "guide", "tips", "checklist", "erklärt"],
    "local": ["in der nähe", "nahe", "umgebung", "stadt", "ort", "vor ort", "near me",
              "in berlin", "in münchen", "in hamburg", "in köln", "in frankfurt", "in stuttgart",
              "gutachter", "werkstatt", "anwalt", "arzt"],
}


def classify_intent(keyword: str) -> str:
    k = keyword.lower()
    for intent, markers in INTENT_MARKERS.items():
        if any(m in k for m in markers):
            return intent
    return "informational"


def _stems(term: str) -> str:
    for suf in ("en", "er", "es", "e", "s", "ing"):
        if term.endswith(suf) and len(term) - len(suf) >= 4:
            return term[:-len(suf)]
    return term


def cluster_terms(terms: list, n_clusters: int = 4) -> list:
    clusters = {}
    for t in terms:
        clusters.setdefault(_stems(t.lower()), set()).add(t)
    ranked = sorted(clusters.values(), key=len, reverse=True)
    return [sorted(c) for c in ranked[:n_clusters]]


def content_brief(topic: str, keyword: str = "") -> str:
    focus = keyword or topic
    intent = classify_intent(focus)
    intent_label = {"transactional": "Transaktional (Kauf/Anfrage)",
                    "informational": "Informational (Ratgeber/Wissen)",
                    "local": "Lokal (Vor-Ort-Suche)"}[intent]
    city = ""
    for w in focus.split():
        if w and w[0].isupper() and w.lower() not in STOPWORDS:
            city = w
    if not city:
        city = topic.split()[-1] if topic.split() else "Ihrer Region"
    core_terms = [w.lower() for w in words(focus) if w.lower() not in STOPWORDS]
    lines = [f"# Content-Brief: {topic}", "",
             f"- **Fokus-Keyword:** {focus}",
             f"- **Suchintention:** {intent_label}",
             f"- **Zielwortzahl:** {'1200–1800' if intent == 'informational' else '800–1200'} Wörter", "",
             "## 1. Suchintention",
             "Beantworte die Frage hinter dem Keyword direkt im ersten Absatz.",
             f"Kernbegriffe, die natürlich vorkommen sollten: {', '.join(core_terms) or focus}", "",
             "## 2. Struktur (H2/H3)"]
    if intent == "local":
        lines += ["- **H2:** {Thema} in {Ort} – das Wichtigste zuerst",
                  "- **H2:** So läuft der Ablauf / die Leistung ab",
                  "- **H2:** Kosten & Preise (transparente Spanne)",
                  "- **H2:** Häufige Fragen (FAQ) mit lokalen Antworten",
                  "- **H3 (in FAQ):** Antworten als kurze, zitierfähige Absätze"]
    elif intent == "transactional":
        lines += ["- **H2:** {Angebot} – Leistungen & Preise im Überblick",
                  "- **H2:** Ablauf Schritt für Schritt",
                  "- **H2:** Warum {Unternehmen} / Referenzen",
                  "- **H2:** Jetzt anfragen (CTA mit Kontakt)"]
    else:
        lines += ["- **H2:** {Thema} einfach erklärt",
                  "- **H2:** Schritt-für-Schritt-Anleitung",
                  "- **H2:** Typische Fehler & wie man sie vermeidet",
                  "- **H2:** FAQ / häufige Fragen"]
    lines += ["", "## 3. Meta-Entwurf",
              f"- **Title:** {focus[:55]}",
              f"- **Description:** {focus} – {('kompakt erklärt mit Beispielen' if intent == 'informational' else 'Leistungen, Ablauf und Preise im Überblick')}. Jetzt mehr erfahren.",
              "", "## 4. Gegencheck (Zitierfähigkeit)",
              "Vor Veröffentlichung mit `./seo local <url>` prüfen, ob NAP (Name, Adresse, Telefon)",
              "und Impressum vorhanden sind — essenziell für lokale/vertrauenswürdige Inhalte.", "",
              "## 5. Frühindikatoren für Erfolg",
              "- Indexierung der URL in der Search Console (innerhalb von Tagen)",
              "- Impressions für den Fokus-Begriff (erste Woche)",
              "- CTR > 3 % für die Hauptphrase nach 2–3 Wochen"]
    brief = "\n".join(lines)
    thema = topic.strip()
    if city and city.lower() in thema.lower():
        thema = re.sub(rf"\s*{re.escape(city)}\s*$", "", thema).strip()
    return (brief.replace("{Thema}", thema).replace("{Ort}", city)
            .replace("{Angebot}", thema).replace("{Unternehmen}", "Ihr Unternehmen"))


def cluster_report(keyword: str, page_terms: list) -> str:
    terms = list(dict.fromkeys([keyword] + page_terms))
    clusters = cluster_terms(terms)
    lines = [f"# Keyword-Cluster: {keyword}",
             f"*Intent: {classify_intent(keyword)} · ohne Fremdindex (keine Suchvolumina)*", ""]
    for i, c in enumerate(clusters, 1):
        lines.append(f"## Cluster {i}: {', '.join(c[:6])}")
        lines.append(f"- Kernbegriff: **{c[0]}**")
        lines.append(f"- Verwandte Begriffe: {', '.join(c[1:8]) if len(c) > 1 else '—'}")
        lines.append("")
    return "\n".join(lines)
