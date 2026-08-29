"""Visual-/Render-Prüfungen: JS-Hydration, Lazy-Load, Console, Netzwerk."""
from __future__ import annotations

from lib.fetch import HttpResult, RenderResult
from lib.htmlutil import soup, words
from lib.report import CategoryResult, Finding, make_recommendation, score_category


def run(http: HttpResult, render: RenderResult) -> CategoryResult:
    cat = CategoryResult(category="visual")
    if render.error:
        cat.recommendations.append(make_recommendation("visual", "critical", "Rendering fehlgeschlagen",
            f"Playwright konnte die Seite nicht rendern: {render.error[:120]}",
            "Zuerst klären (Blocking/JS-Fehler), sonst sind alle visuellen Checks verrauscht.",
            "Die Seite bleibt für Nutzer/Bots ohne JS leer.", "Rendering liefert konsistent sichtbaren Inhalt."))
        cat.score = 0
        return cat

    raw_soup = soup(http.html)
    raw_text = raw_soup.get_text(" ", strip=True)
    rendered_text = render.body_text
    raw_words = len(words(raw_text))
    rendered_words = len(words(rendered_text))

    if raw_words > 0 and rendered_words > raw_words * 1.5:
        cat.recommendations.append(make_recommendation("visual", "warning", "Inhalte erst nach JS/Hydration sichtbar",
            f"Raw-HTML hat {raw_words} Wörter, gerendert {rendered_words} (+{(rendered_words/raw_words - 1)*100:.0f}%).",
            "Prüfen, ob kritische Inhalte serverseitig gerendert werden (SSR/SSG).",
            "Google (ohne JS-Vollausführung) sieht weniger Content als der Nutzer.",
            "Raw-HTML und gerenderter Inhalt decken sich weitgehend."))
    elif raw_words > 0 and rendered_words < raw_words * 0.5:
        cat.recommendations.append(make_recommendation("visual", "warning", "Gerenderter Text deutlich kleiner als HTML",
            f"Raw {raw_words} vs. gerendert {rendered_words} Wörter — möglicherweise versteckter/geblockter Content.",
            "Prüfen, ob Content per JS ausgeblendet wird.", "Google wertet versteckten Text ggf. als Cloaking/Spam.",
            "Gerendert sichtbarer Text entspricht dem erwarteten Inhalt."))

    if render.console_errors:
        cat.recommendations.append(make_recommendation("visual", "warning", "JavaScript-Console-Fehler",
            f"{len(render.console_errors)} Fehler, z.B. {render.console_errors[0][:100]}",
            "Nach Content-Fixes; JS-Fehler können Hydration/Layout brechen.",
            "Interaktive Elemente funktionieren nicht; CLS steigt.", "Console loggt 0 Fehler beim Laden."))

    if render.failed_requests:
        cat.recommendations.append(make_recommendation("visual", "warning", "Fehlgeschlagene Netzwerk-Requests",
            f"{len(render.failed_requests)} Requests, z.B. {render.failed_requests[0][:100]}",
            "Nach Ressourcen-Audit; kaputte Assets senken Ladezeit/UX.", "Bilder/Skripte laden nicht; Seite wirkt unfertig.",
            "Keine 4xx/5xx-Assets im Network-Panel."))

    if render.load_ms and render.load_ms > 4000:
        cat.recommendations.append(make_recommendation("visual", "warning", "Hohe Ladezeit (Lab-Schätzung)",
            f"load ≈ {render.load_ms:.0f} ms (ohne PSI nur Laborwert).",
            "Mit PageSpeed-Insights-Key verifizieren (CrUX-Felddaten).",
            "Nutzer springen ab (hohe Bounce-Rate).", "Lab-Load sinkt unter ~2.5 s; CrUX zeigt LCP < 2.5 s."))
    else:
        cat.findings.append(Finding("visual", "pass", "Ladezeit im Rahmen (Lab)",
                                    f"load ≈ {render.load_ms:.0f} ms, dom-ready ≈ {render.dom_ready_ms:.0f} ms.",
                                    "Laborwerte, keine CrUX-Felddaten."))

    if not rendered_text.strip():
        cat.recommendations.append(make_recommendation("visual", "critical", "Kein sichtbarer gerenderter Text",
            "Gerenderte Seite enthält keinen sichtbaren Body-Text.", "Sofort klären — Seite könnte für Nutzer leer sein.",
            "Nutzer sehen eine leere/weiße Seite.", "Sichtbarer Text ist im gerenderten DOM vorhanden."))

    cat.findings.append(Finding("visual", "info", "Render-Vergleich",
                                f"Raw: {raw_words} Wörter, gerendert: {rendered_words} Wörter.",
                                f"Title (gerendert): {render.title[:80]}"))
    cat.score = score_category(cat)
    return cat
