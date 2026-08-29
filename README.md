# seo-audit — Local SEO & Technical Audit Toolkit

A production-grade, **Claude-Code-style SEO orchestrator** (a native port of
[AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) v2.2.5, MIT)
that runs entirely in your own environment — **no Claude Code, no plugin marketplace**,
no third-party SaaS required.

It combines **deterministic measurement** (own Python specialists + 53 ported
scripts) with **LLM-driven judgment** (24 sub-skills + 18 agent prompts), and
synthesises everything into one weighted, prioritised report.

---

## What it does

A full audit is split into two layers:

| Layer | What it is | How it runs |
|-------|------------|-------------|
| **Measurement** | 5 Python specialists + 53 curated scripts | `./seo <command>` |
| **Judgment** | 24 sub-skills + 18 agent prompts (E-E-A-T, GEO/AIO, Local/GBP, SXO, …) | Agent executes via `subagent`/`workflow` |

Every recommendation carries the four claude-seo fields:
**Observation → Dependency → Failure signal → Early indicator.**

---

## Quick start

```bash
cd seo-toolkit
./setup.sh          # installs workspace-local deps + Playwright Chromium
./seo doctor        # environment health check

./seo audit https://example.com        # full weighted audit
./seo technical <url>                   # technical SEO (9 categories)
./seo page <url>                        # on-page / content signals
./seo schema <url>                      # schema.org / LocalBusiness
./seo local <url>                       # local / NAP signals
./seo visual <url>                      # render, hydration, console errors
./seo sitemap <url>                     # sitemap discovery & validation
./seo content <url|file>                # QRG content-quality scoring
./seo backlinks <url>                   # free backlink sources
./seo cluster <keyword>                 # keyword clustering
./seo content-brief <topic> [keyword]   # content brief
./seo drift baseline|compare|history <url>
./seo google <sub> [args]               # PSI / CrUX / GSC / GA4 (key required)
./seo run <script.py> [args]            # run any of the 53 scripts directly
./seo list                              # enumerate scripts, skills, extensions
```

### Gated multi-agent fan-out

`./seo audit` detects the business type, then spawns only the **relevant**
sub-agents in parallel (never all 18):
- **Always:** technical, content/E-E-A-T, schema, page, sxo, geo
- **By industry:** saas → cluster/programmatic · local-service → local/maps
  · ecommerce → ecommerce · publisher → cluster/images · agency → competitor-pages
- **By credential:** google, backlinks, dataforseo, firecrawl (only with keys)

Ready-made workflow: `audit-fanout.workflow.js`.

---

## Architecture

```
seo-toolkit/
├── seo.py               # CLI orchestrator (weighted score, redaction, gating)
├── lib/                 # measurement core (fetch, report, drift, checks_*)
├── scripts/             # 53 ported measurement scripts
├── skills/              # 24 sub-skill prompt packs + reference knowledge
├── agents/              # 18 specialist agent prompts
├── extensions/          # DataForSEO, Firecrawl, Ahrefs, Bing, Banana, …
├── schema/ pdf/ data/   # support assets
└── audit-fanout.workflow.js  # reproducible parallel fan-out
```

**Weighted SEO Health Score** (claude-seo parity): Technical 22% · Content 23%
· On-Page 20% · Schema 10% · Performance 10% · AI-Readiness 10% · Images 5%.

**Sandbox-safe runtime:** workspace-local `pylibs/` (pinned to known-good
`lxml==5.4.0`, `requests==2.32.5`, `playwright==1.55.0`) and `browsers/`.

---

## Requirements

- Python 3.10+ on macOS/Linux
- `requests`, `beautifulsoup4`, `lxml`, `playwright` (see `requirements.txt`)

---

## Key-gated features

Google APIs (PageSpeed, CrUX, GSC, GA4), DataForSEO, Firecrawl, Ahrefs, Bing and
Banana are **ported but require their own credentials**. Without them the core
measurement still works fully.

---

## Attribution & License

Ported from [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)
(MIT, © Agrici Daniel). Original `LICENSE`/`LICENSE.txt` files are preserved.
The orchestrator, `lib/`, and this wrapper are also MIT.
