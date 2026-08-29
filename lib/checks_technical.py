"""Technische SEO-Prüfungen (statisch, auf HTTP-Antwort + HTML)."""
from __future__ import annotations

from urllib.parse import urlparse

from lib.fetch import HttpResult, domain_of, robots_txt, sitemap_urls
from lib.htmlutil import soup, meta_content, title_text, h1s, heading_counts, link_attr
from lib.report import CategoryResult, Finding, make_recommendation, score_category

TITLE_MIN, TITLE_MAX = 30, 60
DESC_MIN, DESC_MAX = 70, 160


def run(http: HttpResult) -> CategoryResult:
    cat = CategoryResult(category="technical")
    if http.error:
        cat.findings.append(Finding("technical", "critical", "Seite nicht erreichbar",
                                    f"HTTP-Fehler: {http.error}", ""))
        cat.score = 0
        return cat
    s = soup(http.html)
    title = title_text(s)
    desc = meta_content(s, "description")
    canon = s.find("link", rel="canonical")
    meta_robots = meta_content(s, "robots")
    viewport = s.find("meta", attrs={"name": "viewport"})
    html_tag = s.find("html")
    lang = html_tag.get("lang") if html_tag else None
    h1_list = h1s(s)
    headings = heading_counts(s)
    imgs = s.find_all("img")
    imgs_missing_alt = [i for i in imgs if not (i.get("alt") or "").strip()]
    og_title = meta_content(s, "og:title")
    og_image = meta_content(s, "og:image")
    twitter_card = meta_content(s, "twitter:card")

    if not title:
        cat.recommendations.append(make_recommendation("technical", "critical", "Title-Tag fehlt",
            "Kein <title> im <head> gefunden.", "Zuerst beheben; H1 und Description referenzieren den Title.",
            "Seite erscheint mit generischem/URL-Titel.", "Search Console zeigt 'Title fehlt' nicht mehr an."))
    elif len(title) < TITLE_MIN:
        cat.recommendations.append(make_recommendation("technical", "warning", "Title zu kurz",
            f"Title hat {len(title)} Zeichen (empfohlen {TITLE_MIN}–{TITLE_MAX}).", "Keine.",
            "CTR sinkt, weil der Titel die Suchintention nicht abdeckt.", "CTR in der Search Console steigt nach Titel-Update."))
    elif len(title) > TITLE_MAX:
        cat.recommendations.append(make_recommendation("technical", "warning", "Title zu lang",
            f"Title hat {len(title)} Zeichen (wird ggf. abgeschnitten).", "Keine.",
            "Titel wird mit '…' abgeschnitten.", "Vollständiger Titel erscheint ohne Kürzung."))
    else:
        cat.findings.append(Finding("technical", "pass", "Title-Länge OK", f"{len(title)} Zeichen.", title[:80]))

    if not desc:
        cat.recommendations.append(make_recommendation("technical", "warning", "Meta-Description fehlt",
            "Keine <meta name='description'> gefunden.", "Nach dem Title optimieren.",
            "Google zeigt ein selbst gewähltes Snippet.", "Eigene Description erscheint im SERP-Snippet."))

    if not canon:
        cat.recommendations.append(make_recommendation("technical", "critical", "Canonical fehlt",
            "Kein <link rel='canonical'> vorhanden.", "Vor Indexierungsfragen klären.",
            "Duplicate-Content-Risiko.", "Search Console meldet 'doppelte Seiten ohne Canonical' seltener."))
    else:
        c = canon.get("href", "")
        cat.findings.append(Finding("technical", "pass", "Canonical vorhanden", f"Canonical zeigt auf: {c}", ""))

    if http.history:
        hops = " → ".join(f"{st} {u}" for st, u in http.history)
        cat.findings.append(Finding("technical", "info", "Redirect-Kette", f"{len(http.history)} Hop(s).", hops))
    if urlparse(http.final_url).scheme != "https":
        cat.recommendations.append(make_recommendation("technical", "critical", "Keine HTTPS-Auslieferung",
            f"Endgültige URL nutzt {urlparse(http.final_url).scheme} statt https.", "Vor anderen Optimierungen beheben.",
            "Browser zeigt 'Nicht sicher'.", "Alle URLs laufen über HTTPS."))

    if not viewport:
        cat.recommendations.append(make_recommendation("technical", "critical", "Viewport-Meta fehlt",
            "Keine <meta name='viewport'> — Mobil-Tauglichkeit gefährdet.", "Vor Mobile-Core-Web-Vitals.",
            "Mobile Nutzer sehen eine unskalierte Ansicht.", "Mobile-Friendly-Test meldet 'verwendet Viewport'."))
    if not lang:
        cat.recommendations.append(make_recommendation("technical", "warning", "lang-Attribut fehlt",
            "<html> hat kein lang-Attribut.", "Keine.",
            "Screenreader/Suchmaschine kann Sprache nicht sicher zuordnen.", "<html lang='de'> ist gesetzt."))

    if len(h1_list) == 0:
        cat.recommendations.append(make_recommendation("technical", "critical", "Kein H1",
            "Keine <h1>-Überschrift gefunden.", "Nach Title- und Content-Brief abstimmen.",
            "Die Seite hat keine klare Hauptüberschrift.", "Genau ein beschreibendes H1 ist vorhanden."))
    elif len(h1_list) > 1:
        cat.recommendations.append(make_recommendation("technical", "warning", "Mehrere H1",
            f"{len(h1_list)} H1 gefunden.", "Mit Content-Struktur abstimmen.",
            "Mehrdeutige Seitenstruktur.", "Genau ein H1 pro Seite."))

    if imgs_missing_alt:
        cat.recommendations.append(make_recommendation("technical", "warning", "Bilder ohne Alt-Text",
            f"{len(imgs_missing_alt)} von {len(imgs)} Bildern ohne alt-Attribut.",
            "Nach Content-Optimierung; wichtig für Bildsuche/Barrierefreiheit.",
            "Bilder ranken nicht in der Bildsuche.", "Alle inhaltstragenden Bilder haben beschreibende Alt-Texte."))

    if not og_title and not og_image:
        cat.recommendations.append(make_recommendation("technical", "warning", "Open-Graph-Daten fehlen",
            "Keine og:title/og:image — Social-Sharing-Snippets unkontrolliert.",
            "Nach Title/Description setzen.", "Geteilte Links zeigen kein Vorschaubild.",
            "Social-Sharing-Debugger zeigt korrektes Vorschaubild."))
    if not twitter_card:
        cat.findings.append(Finding("technical", "info", "twitter:card fehlt", "Keine twitter:card-Meta.", ""))

    domain = domain_of(http.final_url)
    robots = robots_txt(domain)
    if not robots:
        cat.recommendations.append(make_recommendation("technical", "warning", "robots.txt fehlt oder leer",
            f"Keine robots.txt unter {domain}/robots.txt.", "Vor Sitemap-Einreichung klären.",
            "Crawler haben keine Anweisungen.", "robots.txt liefert 200 und verweist auf die Sitemap."))
    if "noindex" in (meta_robots or "").lower():
        cat.recommendations.append(make_recommendation("technical", "critical", "Seite auf noindex",
            f"meta robots = '{meta_robots}' — Seite wird nicht indexiert.", "Sofort klären.",
            "Die Seite erscheint nicht in Google.", "URL ist in der Search Console indexierbar."))

    cat.score = score_category(cat)
    return cat
