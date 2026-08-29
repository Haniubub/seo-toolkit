---
name: seo-audit
description: >-
  Vollständiger SEO-Orchestrator (Port von claude-seo v2.2.5): technische SEO,
  On-Page, Schema, E-E-A-T, GEO/AI-Overview, Local/GBP, Backlinks, E-Commerce,
  hreflang/i18n, Sitemap, Bilder-SEO, Keyword-Clustering, Content-Briefs,
  Drift-Tracking und Google-APIs (PSI/CrUX/GSC) über ein lokales Python-Toolkit
  (53 Skripte) + 24 Sub-Skills + 18 Agents. Befunde mit priorisiertem
  Aktionsplan und 4-Felder-Empfehlungen.
whenToUse: >-
  SEO-Audits, technische SEO, Schema.org/JSON-LD, E-E-A-T, GEO/AI-Overview,
  Local/GBP, Backlinks, E-Commerce, hreflang/i18n, Sitemap, Bilder-SEO,
  Keyword-Clustering, Content-Briefs, Drift-Tracking, Google-API-Reports.
---

# SEO-Audit-Orchestrator (Port von claude-seo)

Natives Tool unter `seo-toolkit/`. Zwei Schichten:
- **Messung** = `./seo <cmd>` (Python: eigene Specialists + 53 portierte Skripte).
- **Urteil** = Sub-Skills (`skills/`) + Agents (`agents/`), die ich als Agent
  ausführe, ergänzt durch `web_search` und `subagent`-Fan-out.

## Wichtig zuerst

1. **Erst breit, dann tief:** `./seo audit <url>` zuerst, dann gezielt
   nachbohren. Wer mit Einzelbefehlen startet, optimiert Symptome statt Ursachen.
2. **Erst einrichten:** Wenn `./seo doctor` einen Fehler meldet → `./setup.sh`.
   Chromium liegt workspace-lokal; gelegentliche Sandbox-Hänger werden per
   Subprozess-Timeout abgefangen (einfach erneut versuchen).
3. **Jede Empfehlung trägt 4 Felder:** Beobachtung → Abhängigkeit →
   Misserfolgssignal → Frühindikator. Feld 2 = Reihenfolge, Feld 3 = Erfolgskontrolle.

## Befehlsfläche

| Befehl | Schicht | Was es tut |
|---|---|---|
| `./seo doctor` | Messung | Umgebungs-Check |
| `./seo audit <url>` | Messung+Urteil | Gesamtbefund (Specialists + Sitemap + HTML-Struktur) |
| `./seo technical <url>` | Messung | Technisch (9 Kategorien via `checks_technical`) |
| `./seo page <url>` | Messung | On-Page (Content, Links, Keyword-Signale) |
| `./seo schema <url>` | Messung | JSON-LD/LocalBusiness erkennen+validieren |
| `./seo local <url>` | Messung | Lokal/NAP (entspricht claude-seo `local`) |
| `./seo visual <url>` | Messung | Render/Hydration, Console, Ladezeit (Lab) |
| `./seo sitemap <url>` | Messung | Sitemap erkennen/validieren (`sitemap_discovery.py`) |
| `./seo content <url\|datei>` | Messung | QRG-Content-Qualität (`content_quality.py`) |
| `./seo hreflang <url>` | Messung | hreflang/i18n extrahieren (`parse_html.py`) |
| `./seo backlinks <url>` | Messung | Freie Quellen (Moz/Bing/CommonCrawl); Premium: DataForSEO |
| `./seo cluster <keyword>` | Messung | Heuristisches Clustering (SERP-basiert: `skills/seo-cluster`) |
| `./seo content-brief <topic> [kw]` | Messung | Content-Brief |
| `./seo drift baseline\|compare\|history <url>` | Messung | Zeitreihe |
| `./seo google <sub> [args]` | Messung | PSI/CrUX/GSC/GA4/Indexing/Keyword-Planner (Key nötig) |
| `./seo run <script.py> [args]` | Messung | Beliebiges der 53 Skripte direkt |
| `./seo list` | — | Skripte + Sub-Skills + Extensions auflisten |

## Urteils-Befehle (Agent führt Sub-Skill aus)

Diese brauchen LLM-Urteil, nicht nur Messung. Ich lade die passende
`skills/<name>/SKILL.md` und führe sie aus (bei Bedarf mit `subagent` parallel):

- **E-E-A-T / Content-Qualität** → `skills/seo-content/SKILL.md` (+ `agents/seo-content.md`)
- **GEO / AI Overviews** (ChatGPT/Perplexity/AI Overviews) → `skills/seo-geo/SKILL.md`
- **Local/GBP** (Google Business, Zitate, Reviews, Map Pack) → `skills/seo-local/SKILL.md`
- **Maps-Intelligence** (Geo-Grid, GBP-Audit) → `skills/seo-maps/SKILL.md`
- **SXO** (Search Experience, Personas, User Stories) → `skills/seo-sxo/SKILL.md`
- **Plan** (Strategie je Branche) → `skills/seo-plan/SKILL.md`
- **Programmatic SEO** → `skills/seo-programmatic/SKILL.md`
- **Competitor-Pages** → `skills/seo-competitor-pages/SKILL.md`
- **E-Commerce** → `skills/seo-ecommerce/SKILL.md`
- **Bilder-SEO** → `skills/seo-images/SKILL.md`
- **FLOW-Framework** → `skills/seo-flow/SKILL.md`
- **Cluster (SERP-basiert)** → `skills/seo-cluster/SKILL.md`

## Orchestrierung (`audit`) — gated Multi-Agent-Fan-out

**Zwei Schranken (gating), dann parallel:**

1. **Branche erkennen** (SaaS / local-service / ecommerce / publisher / agency / other)
   aus Homepage-Signalen (`./seo audit` druckt sie bereits).

2. **Kategorie-Menge bestimmen:**
   - **Immer** (branchenunabhängig): `technical`, `content` (E-E-A-T), `schema`, `page`, `sxo`, `geo` (GEO/AI-Overview)
   - **Nach Branche:**
     | Branche | zusätzliche Agents |
     |---|---|
     | saas | `cluster`, `programmatic` |
     | local-service | `local`, `maps` |
     | ecommerce | `ecommerce` |
     | publisher | `cluster`, `images` |
     | agency | `competitor-pages` |
     | other | — |
   - **Nach Credentials** (nur wenn Key/Zugang vorhanden): `google`, `backlinks`, `dataforseo`, `firecrawl`

3. **PARALLEL ausführen:** Diese Kategorien als **echte parallele Subagenten**
   starten (via `subagent`-Tool oder `workflow`-Skript `audit-fanout.workflow.js`).
   Jeder Subagent: lädt seine `skills/seo-<kategorie>/SKILL.md`, führt die
   Messungen über `./seo <cmd>` aus, liefert strukturierte Findings mit den
   4 Feldern (Beobachtung → Abhängigkeit → Misserfolgssignal → Frühindikator).

4. **Synthese im Haupt-Agent:** alle Subagent-Ergebnisse zu EINEM Befund mit
   **gewichtetem** Score zusammenführen (in `lib/report.py`): Technical 22 % ·
   Content 23 % · On-Page 20 % · Schema 10 % · Performance 10 % ·
   AI-Search-Readiness 10 % · Images 5 %.

5. **Aktionsplan** mit Abhängigkeits-Sortierung + Falsifizierbarkeit je Empfehlung.

**Warum gated:** ein normaler Audit startet so nur ~7–10 Agents statt 18 —
   `ecommerce` nie für eine Werkstatt, `google` nie ohne Key.

## Qualitäts-Gates (nicht ignorieren)

- **30+ Location-Seiten** → Warnung (60 % Unique-Content erzwingen); **50+ → Hard Stop**.
- **HowTo-Schema nie empfehlen** (seit Sept 2023 deprecated).
- **FAQ-Schema:** Rich Results seit 7. Mai 2026 für alle Sites eingestellt → nur
  Info-Hinweis, keine neuen FAQPage für SERP-Nutzen empfehlen; für echtes Q&A QAPage.
- **Core Web Vitals immer INP, nie FID.**

## Referenzdateien (bei Bedarf laden)

- `skills/seo/references/cwv-thresholds.md` · `eeat-framework.md` · `quality-gates.md`
  · `schema-types.md` · `local-seo-signals.md` · `thinking-framework.md`
  · `backlink-quality.md` · `free-backlink-sources.md`

## Grenzen (ehrlich)

- **Ohne Google-Key:** Ladezeit = Laborschätzung, kein CrUX/PSI/GSC.
- **Ohne Fremdindex:** keine Suchvolumina/Backlinks (DataForSEO/Ahrefs brauchen Keys).
- **Extensions** (DataForSEO, Firecrawl, Ahrefs, Bing, Banana, profound, seranking,
  unlighthouse) sind portiert, laufen aber erst mit ihren Credentials.
- **Scroll-/Hydrations-Inhalte** bleiben verrauscht → `visual` als Quervergleich.
