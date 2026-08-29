---
name: seo-audit
description: >-
  Run a full, weighted local & technical SEO audit on any website — entirely
  local, no SaaS, no per-domain pricing. Measures 8 discipline areas with a
  Python CLI (technical, on-page, schema.org/JSON-LD, local/GBP, Core Web
  Vitals, GEO/AI-Overview, content/E-E-A-T, images, sitemap, hreflang, content
  briefs, keyword clustering, drift, and Google APIs), then synthesises the
  findings into one prioritised report with weighted scoring, dependency-ordered
  actions and falsifiable recommendations.
whenToUse: >-
  Any request to audit or improve a website's search visibility, technical SEO,
  schema.org markup, E-E-A-T/content quality, local SEO or Google Business
  Profile, GEO/AI-Overview readiness, Core Web Vitals, sitemap/hreflang,
  keyword clustering, content briefs, or drift tracking.
---

# seo-audit — local & technical SEO audit toolkit

A two-layer audit engine. **Measurement** is deterministic (a Python CLI + 53
curated scripts). **Judgment** is where the model interprets those findings and
writes the plan. Both stay on your machine: no API keys for the core, no
third-party SaaS, no per-domain pricing.

## Use this first

1. **Broad, then deep.** Run `./seo audit <url>` once, then drill into the
   highest-impact findings. Starting with single commands optimises symptoms
   instead of root causes.
2. **Setup first.** If `./seo doctor` reports an error, run `./setup.sh`. Chromium
   is workspace-local; occasional sandbox hangs are caught by a subprocess
   timeout — just retry.
3. **Recommendations carry 4 fields.** Observation → Dependency → Failure signal →
   Early indicator. Field 2 sets the order, field 3 tells you how you'd know it
   worked.

## Command surface

| Command | Measures |
|---------|----------|
| `./seo doctor` | Environment health check |
| `./seo audit <url>` | Full weighted verdict (specialists + sitemap + structure) |
| `./seo technical <url>` | Technical SEO (9 categories) |
| `./seo page <url>` | On-page: content, links, keyword signals |
| `./seo schema <url>` | JSON-LD / LocalBusiness detection + validation |
| `./seo local <url>` | Local / NAP consistency |
| `./seo visual <url>` | Render, hydration, console errors, load time (lab) |
| `./seo sitemap <url>` | Sitemap discovery + validation |
| `./seo content <url\|file>` | QRG-style content-quality scoring |
| `./seo hreflang <url>` | hreflang / i18n extraction |
| `./seo backlinks <url>` | Free sources (Moz/Bing/Common Crawl); premium via DataForSEO |
| `./seo cluster <keyword>` | Keyword clustering |
| `./seo content-brief <topic> [kw]` | Content brief |
| `./seo drift baseline\|compare\|history <url>` | Time-series drift |
| `./seo google <sub> [args]` | PSI / CrUX / GSC / GA4 (key required) |
| `./seo run <script.py> [args]` | Run any of the 53 scripts directly |
| `./seo list` | Enumerate scripts, sub-skills, extensions |

## Judgment layer

For anything that needs interpretation — not just measurement — load the matching
sub-skill and execute it (optionally in parallel via `subagent`):

- **E-E-A-T / content quality** → `skills/seo-content/SKILL.md`
- **GEO / AI Overviews** → `skills/seo-geo/SKILL.md`
- **Local / GBP** → `skills/seo-local/SKILL.md`
- **Maps intelligence** → `skills/seo-maps/SKILL.md`
- **SXO** (search experience, personas) → `skills/seo-sxo/SKILL.md`
- **Strategy per industry** → `skills/seo-plan/SKILL.md`
- **Programmatic SEO** → `skills/seo-programmatic/SKILL.md`
- **Competitor pages** → `skills/seo-competitor-pages/SKILL.md`
- **E-commerce** → `skills/seo-ecommerce/SKILL.md`
- **Image SEO** → `skills/seo-images/SKILL.md`
- **FLOW framework** → `skills/seo-flow/SKILL.md`
- **Cluster (SERP-based)** → `skills/seo-cluster/SKILL.md`

## Orchestration — gated multi-agent fan-out

Only as many agents as the site actually needs (typically 7–10, never all 18):

1. **Detect business type** (SaaS / local-service / ecommerce / publisher /
   agency / other) from homepage signals.
2. **Choose the category set:**
   - **Always:** technical, content (E-E-A-T), schema, page, sxo, geo
   - **By industry:** saas → cluster/programmatic · local-service → local/maps
     · ecommerce → ecommerce · publisher → cluster/images
     · agency → competitor-pages
   - **By credential:** google, backlinks, dataforseo, firecrawl (only with keys)
3. **Run in parallel.** Each subagent loads its `skills/seo-<category>/SKILL.md`,
   runs measurement via `./seo <cmd>`, and returns structured findings with the
   4 fields.
4. **Synthesise** into one weighted score (in `lib/report.py`): Technical 22% ·
   Content 23% · On-Page 20% · Schema 10% · Performance 10% ·
   AI-Readiness 10% · Images 5%.
5. **Action plan** sorted by dependency, with a falsifiability check per
   recommendation.

## Quality gates (do not ignore)

- **30+ location pages** → warn (enforce 60% unique content); **50+ → hard stop**.
- **Never recommend HowTo schema** (deprecated since Sept 2023).
- **FAQ schema:** rich results withdrawn for all sites on 7 May 2026 → note only;
  use QAPage for genuine Q&A.
- **Core Web Vitals always INP, never FID.**

## Honest limits

- **Without a Google key:** load time is a lab estimate, no CrUX/PSI/GSC data.
- **Without third-party index:** no search volumes/backlink graph
  (DataForSEO/Ahrefs/Bing need their own keys).
- **Extensions** (DataForSEO, Firecrawl, Ahrefs, Bing, Banana, Profound,
  SE Ranking, Unlighthouse) are ported but only work once you supply credentials.
- **Scroll/hydration content** stays noisy → use `visual` as a cross-check.

## Cost

The measurement layer is pure local Python — **$0 in tokens**. Only the LLM
interpretation costs anything, which is typically **~12×–30× cheaper** than the
equivalent Claude-based audit. See the project README for the worked example.
