# SEO-Toolkit (Port von claude-seo)

Vollständiger SEO-Orchestrator, der das Open-Source-Projekt
**[AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)** (v2.2.5, MIT)
nativ in diese Umgebung portiert — ohne Claude Code, ohne Plugin-Marketplace.

Zwei Schichten:
- **Messung** = `./seo <cmd>` (eigene Specialists + 53 portierte Python-Skripte).
- **Urteil** = 24 Sub-Skills (`skills/`) + 18 Agents (`agents/`), ausgeführt vom Agent (LLM).

## Einrichtung
```bash
cd seo-toolkit
./setup.sh        # prüft Abhängigkeiten + installiert Chromium in browsers/
./seo doctor      # Umgebungs-Check
```
Python: vorhandenes `python3` + workspace-lokales `pylibs/` (trafilatura, openpyxl, …).
Gepinnt auf sandbox-sichere Versionen (lxml 5.4.0, requests 2.32.5, playwright 1.55.0).

## Befehle (Messung)
| Befehl | Zweck |
|---|---|
| `./seo doctor` | Umgebungs-Check |
| `./seo audit <url>` | Gesamtbefund (Specialists parallel + Sitemap + HTML-Struktur) |
| `./seo technical\|page\|schema\|local\|visual <url>` | Einzel-Specialists |
| `./seo sitemap <url>` | Sitemap erkennen (sitemap_discovery.py) |
| `./seo content <url\|datei>` | QRG-Content-Qualität |
| `./seo hreflang <url>` | hreflang extrahieren |
| `./seo backlinks <url>` | Freie Backlink-Quellen |
| `./seo cluster <keyword>` / `content-brief <topic>` | Clustering / Brief |
| `./seo drift baseline\|compare\|history <url>` | Zeitreihe |
| `./seo google <sub>` | Google-APIs (Key nötig) |
| `./seo run <script.py> [args]` | Beliebiges der 53 Skripte direkt |
| `./seo list` | Skripte + Sub-Skills + Extensions |

## Urteils-Befehle (Agent)
E-E-A-T, GEO/AI-Overview, Local/GBP, Maps, SXO, Plan, Programmatic, Competitor-Pages,
E-Commerce, Bilder-SEO, FLOW — der Agent lädt die jeweilige `skills/<name>/SKILL.md`.

## 4-Felder-Empfehlung
Beobachtung → Abhängigkeit → Misserfolgssignal → Frühindikator.

## Grenzen
- Ohne Google-Key: Ladezeit nur Laborschätzung.
- Extensions (DataForSEO, Firecrawl, Ahrefs, …) brauchen Credentials.
- Gelegentliche Sandbox-Flakiness wird per Subprozess-Timeout begrenzt.

## Attribution & Lizenz
Portiert aus [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT, © Agrici Daniel).
Eigene Teile (seo.py, lib/, SKILL.md) unter MIT.
