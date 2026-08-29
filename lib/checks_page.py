"""On-Page-Prüfungen: Content, Links, Keyword-Signale."""
from __future__ import annotations

from urllib.parse import urlparse

from lib.fetch import HttpResult
from lib.htmlutil import soup, title_text, h1s, words, top_terms, link_attr
from lib.report import CategoryResult, Finding, make_recommendation, score_category

WORD_MIN = 300
GENERIC_ANCHORS = {"click here", "klick hier", "hier", "here", "mehr", "weiter", "read more",
                   "weiterlesen", "more", "link", "zur website", "jetzt kaufen"}


def run(http: HttpResult, render_text: str = "") -> CategoryResult:
    cat = CategoryResult(category="page")
    if http.error:
        cat.score = 0
        return cat
    s = soup(http.html)
    body_text = s.get_text(" ", strip=True)
    visible = render_text or body_text
    word_count = len(words(visible))
    title = title_text(s)
    h1_list = h1s(s)

    if word_count < WORD_MIN:
        cat.recommendations.append(make_recommendation("page", "warning", "Thin Content",
            f"Nur {word_count} Wörter sichtbarer Text (empfohlen ≥ {WORD_MIN}).",
            "Vor Link-/Schema-Optimierung: erst Inhalt aufbauen.",
            "Die Seite konkurriert nicht für relevante Begriffe.", "Sichtbare Wortzahl und indexierte Begriffe steigen."))
    else:
        cat.findings.append(Finding("page", "pass", "Content-Volumen OK", f"{word_count} Wörter sichtbarer Text.", ""))

    if title and h1_list and title.strip().lower() != h1_list[0].lower():
        cat.findings.append(Finding("page", "info", "Title ≠ H1",
            "Title und H1 unterscheiden sich — kann beabsichtigt sein.",
            f"Title: {title[:60]} | H1: {h1_list[0][:60]}"))

    terms = top_terms(visible, 15)
    if terms:
        cat.findings.append(Finding("page", "info", "Häufigste Terme", f"Top-Terme: {', '.join(terms[:10])}", ""))
    if title and terms:
        title_terms = {w.lower() for w in words(title)}
        if not [t for t in terms if t in title_terms]:
            cat.recommendations.append(make_recommendation("page", "warning", "Title ohne Kern-Term",
                "Der häufigste Content-Term taucht nicht im Title auf.", "Nach Content-Brief das Title-Keyword angleichen.",
                "Relevanzsignal für die Hauptsuchphrase fehlt.", "Hauptkeyword erscheint in Title und H1."))

    links = s.find_all("a", href=True)
    internal = external = 0
    host = urlparse(http.final_url).netloc
    for a in links:
        href = link_attr(a, "href")
        if href.startswith(("http://", "https://")):
            if host in urlparse(href).netloc:
                internal += 1
            else:
                external += 1
        elif href.startswith(("/", "#")):
            internal += 1
    cat.findings.append(Finding("page", "info", "Link-Verteilung", f"{internal} interne, {external} externe Links.", f"Insgesamt {len(links)} Links."))

    generic = [a for a in links if link_attr(a, "href") not in ("", "#") and a.get_text(strip=True).lower() in GENERIC_ANCHORS]
    if generic:
        cat.recommendations.append(make_recommendation("page", "warning", "Generische Ankertexte",
            f"{len(generic)} Link(s) mit generischem Ankertext.", "Nach interner Verlinkungs-Strategie.",
            "Anker geben Crawlern keinen Kontext.", "Ankertexte beschreiben die Zielseite."))

    ids = [t.get("id") for t in s.find_all(attrs={"id": True})]
    dup_ids = {i for i in ids if ids.count(i) > 1}
    if dup_ids:
        cat.recommendations.append(make_recommendation("page", "warning", "Doppelte HTML-IDs",
            f"Mehrfach vergebene IDs: {', '.join(sorted(dup_ids)[:5])}.",
            "Vor JS-/Tracking-Anpassungen.", "JS-Selektoren treffen das falsche Element.", "Jede ID kommt genau einmal vor."))

    cat.score = score_category(cat)
    return cat
