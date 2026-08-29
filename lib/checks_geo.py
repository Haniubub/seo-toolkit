"""Lokale/Geo-Signale: NAP, Geo-Meta, Zitierfähigkeit (Impressum, Öffnungszeiten)."""
from __future__ import annotations

from lib.fetch import HttpResult
from lib.htmlutil import soup, meta_content, phone_numbers, email_addresses, postal_address
from lib.report import CategoryResult, Finding, make_recommendation, score_category


def run(http: HttpResult, render_text: str = "") -> CategoryResult:
    cat = CategoryResult(category="local")
    if http.error:
        cat.score = 0
        return cat
    s = soup(http.html)
    page_text = s.get_text(" ", strip=True)
    full_text = render_text or page_text

    phones = phone_numbers(full_text)
    emails = email_addresses(full_text)
    addresses = postal_address(full_text)
    geo_region = meta_content(s, "geo.region")
    geo_position = meta_content(s, "geo.position")
    icbm = meta_content(s, "ICBM")

    impressum_link = None
    for a in s.find_all("a", href=True):
        txt = (a.get_text(strip=True) or "").lower()
        if "impressum" in txt or "impressum" in (a.get("href") or "").lower():
            impressum_link = a.get("href")
            break

    has_hours = bool(s.find(attrs={"itemprop": "openingHours"})) or ("öffnungszeit" in full_text.lower() or "opening hours" in full_text.lower())
    has_maps = bool(s.find("iframe", attrs={"src": lambda v: v and "google.com/maps" in v})) or ("maps.google" in (http.html or "") or "google.com/maps" in (http.html or ""))

    findings = []
    if phones:
        findings.append(Finding("local", "pass", "Telefonnummer gefunden", f"{len(phones)} Nummer(n): {', '.join(phones[:3])}", ""))
    else:
        cat.recommendations.append(make_recommendation("local", "warning", "Keine Telefonnummer auffindbar",
            "Keine erkennbare Telefonnummer im sichtbaren Text.", "Für lokale Zitierfähigkeit zwingend; vor Schema-NAP-Abgleich.",
            "Nutzer finden keinen direkten Kontaktweg.", "Telefonnummer erscheint als Click-to-Call im sichtbaren Bereich."))

    if emails:
        findings.append(Finding("local", "pass", "E-Mail gefunden", f"{', '.join(emails[:3])}", ""))
    if addresses:
        findings.append(Finding("local", "pass", "Adresse gefunden", f"{', '.join(addresses[:3])}", ""))
    else:
        cat.recommendations.append(make_recommendation("local", "warning", "Keine postalische Adresse erkennbar",
            "Keine PLZ+Ort-Struktur im Text gefunden.", "Mit LocalBusiness-Schema synchronisieren.",
            "Lokale Suchanfragen können den Standort nicht zuordnen.", "Adresse ist sichtbar und deckungsgleich mit Schema/Google Business."))

    if impressum_link:
        findings.append(Finding("local", "pass", "Impressum verlinkt", f"Impressum-Link: {impressum_link}", ""))
    else:
        cat.recommendations.append(make_recommendation("local", "critical", "Impressum nicht gefunden",
            "Kein Link mit 'Impressum' im Ankertext/Href.", "Rechtlich (DE) und als Vertrauenssignal für lokale Suche wichtig.",
            "Rechtliche Abmahnungsgefahr; schwaches Vertrauenssignal.", "Impressum ist im Footer verlinkt und erreichbar."))

    if has_hours:
        findings.append(Finding("local", "pass", "Öffnungszeiten vorhanden", "Öffnungszeiten im Text/Schema erkannt.", ""))
    else:
        cat.findings.append(Finding("local", "info", "Öffnungszeiten nicht erkannt", "Keine Öffnungszeiten gefunden (für lokale Suche nützlich).", ""))
    if has_maps:
        findings.append(Finding("local", "pass", "Google-Maps-Einbettung", "Karten-Einbettung erkannt.", ""))
    if geo_position or icbm or geo_region:
        findings.append(Finding("local", "info", "Geo-Meta-Tags", f"region={geo_region} pos={geo_position or icbm}", ""))

    cat.findings.extend(findings)
    cat.score = score_category(cat)
    return cat
