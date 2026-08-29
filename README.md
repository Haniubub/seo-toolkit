# seo-audit — Local SEO & Technical Audit Toolkit

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![CI](https://github.com/Haniubub/seo-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Haniubub/seo-toolkit/actions)

> **Status:** production-ready port of `claude-seo` v2.2.5 · **v1.0.0**


A production-grade, **local SEO & technical SEO audit toolkit** — a native, self-contained
port of [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) v2.2.5 (MIT) that
runs entirely in your own environment: **no Claude Code, no plugin marketplace, no third-party SaaS**.

Built for **local SEO**, **technical SEO**, **schema.org**, **E-E-A-T**, **GEO / AI Overviews**,
**Google Business Profile (GBP)**, **on-page & content** audits across any industry.

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

## Cost per audit — DeepSeek Harness vs Claude Code

The judgment layer uses an LLM, so a full audit costs real tokens. But the
observable layer is **pure local Python** (53 scripts + `lib/`) — it runs for **$0
in tokens**. The only spend is the LLM reasoning over those findings, and that is
the whole reason this port is worth switching to.

| Model (per 1M tokens — in / out) | Input | Output | **Cost per full audit** |
|---------------------------------|-------|--------|--------------------------|
| Claude Opus 5 | $5.00 | $25.00 | **≈ $1.13** |
| Claude Sonnet 5 | $2.00 | $10.00 | **≈ $0.45** |
| Claude Haiku 4.5 | $1.00 | $5.00 | **≈ $0.23** |
| **DeepSeek V3.2** | **$0.27** | **$0.40** | **≈ $0.04** |

**Worked example** — one full `./seo audit` on a local-service site spawns the
always-on agents (technical, content/E-E-A-T, schema, page, sxo, geo) plus a few
industry-specific ones, then synthesises the weighted report. Measure that as
**100,000 input tokens and 25,000 output tokens** per audit:

```
Claude Opus 5:   (0.10 M × $5)  + (0.025 M × $25)  = $0.50 + $0.625 = $1.13
Claude Sonnet 5: (0.10 M × $2)  + (0.025 M × $10)  = $0.20 + $0.25  = $0.45
DeepSeek V3.2:   (0.10 M × $0.27)+ (0.025 M × $0.40) = $0.027 + $0.01 = $0.037
```

So the same audit costs **≈ $0.04 on DeepSeek** against **≈ $0.45 on Claude
Sonnet** and **≈ $1.13 on Claude Opus** — roughly **12× cheaper** than Sonnet and
**30× cheaper** than Opus. Run 20 sites a day and Claude Opus would bill you
**≈ $22.60** for the LLM judgment alone; DeepSeek does the same for **≈ $0.74**.

The measurement layer never touches the LLM, so a `technical`, `schema` or
`local` check can be **$0** — only the reasoning steps that need judgement cost
anything.

> Prices are indicative list rates as of August 2026 and change frequently.
> DeepSeek rates per [OpenRouter](https://openrouter.ai/deepseek); Claude rates
> per [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
> Token volumes are illustrative of a typical multi-agent audit and vary by site.

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

This project is a **native re-implementation and port** of
[AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) v2.2.5
(MIT, © Agrici Daniel). It does **not** vendor the original repository or run
Claude Code; the upstream toolkit was ported, adapted and rebuilt to run
standalone as a local CLI + agent library in the DeepSeek Harness environment.

Where the measurement logic is derived from claude-seo, the original MIT
copyright and permission notice is preserved in [`LICENSE`](LICENSE) and in the
individual ported script headers.

**This repo's own work** (also MIT, © 2026 seo-audit contributors):

- **Runtime port & integration** — a wrapper/orchestrator that executes the
  toolkit natively as `./seo`, with dependency pinning and a sandbox-safe,
  workspace-local runtime (no global installs, no SaaS).
- **Weighted health scoring** — the 22/23/20/10/10/10/5 category weighting and
  the `overall_score()` renormalisation.
- **Gated multi-agent fan-out** — business-type detection + credential gating so
  only relevant sub-agents spawn, with the reproducible `audit-fanout.workflow.js`.
- **Toolchain hardening** — Playwright headless-render worker with hard subprocess
  timeouts, redaction of secrets, `lib/` measurement core, and curated script set.
- **Packaging, docs & CI** — README, architecture, `./seo doctor`, GitHub Actions
  CI, `CHANGELOG.txt`/release notes.

Both the upstream-derived and the original code are released under the
[MIT License](LICENSE).
