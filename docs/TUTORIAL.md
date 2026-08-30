# Tutorial — audit a site end-to-end in 5 minutes

This walks from a clean install to a full weighted audit plus a focused follow-up.
Everything runs locally; the measurement layer costs $0 in LLM tokens.

## 0. One-time setup

```bash
cd seo-toolkit
./setup.sh          # installs pylibs/ + Chromium, then a smoke test
./seo doctor        # expect "Playwright-Chromium: OK"
```

> If `./seo doctor` times out, that is the headless-Chromium launch flaking under
> the sandbox — just retry. It is not a broken install.

## 1. The broad pass — full weighted audit

```bash
./seo audit https://example.com
```

This does the most work in one call:

- Detects the **business type** (prints `[Branche erkannt: ...]`) and picks the
  category set from it.
- Runs the specialists (technical, on-page, schema, local, visual) **in parallel**.
- Renders the page with Playwright for visual/hydration signals.
- Assigns a **weighted score** across 7 categories (Technical 22% · Content 23% ·
  On-Page 20% · Schema 10% · Performance 10% · AI-Readiness 10% · Images 5%).
- Saves the raw findings to a file and prints extra sitemap + HTML-structure data.

Read the score first, then the top recommendations. Each carries four fields:
**Observation → Dependency → Failure signal → Early indicator.** The dependency
field tells you what to fix first.

## 2. Drill into the biggest gap

The broad pass tells you *where* the problem is. Use a focused command to
understand *what* it is:

```bash
./seo technical https://example.com   # 9 technical categories
./seo schema https://example.com      # JSON-LD / LocalBusiness markup
./seo local https://example.com       # local / NAP consistency
./seo content https://example.com     # QRG-style content quality
./seo sitemap https://example.com     # sitemap discovery + validation
./seo visual https://example.com      # render, hydration, console errors
```

## 3. Judgment on the subjective signals

Measurement is deterministic. For interpretation — E-E-A-T, GEO/AI-Overview
readiness, GBP, strategy — the agent loads the matching sub-skill and reasons
over the measurements:

```bash
./seo geo https://example.com          # GEO / AI Overviews
./seo plan https://example.com         # strategy per industry
./seo competitor-pages https://example.com   # competitive intel
```

## 4. Track change over time

Run a baseline, then compare later to see whether you actually moved the needle:

```bash
./seo drift baseline https://example.com
./seo drift compare https://example.com
./seo drift history https://example.com
```

## 5. Optional enrichment (needs your own credentials)

These work without any key for the core measurement. Only these add third-party
data, and only when you supply credentials:

```bash
./seo google <sub> [args]    # PSI / CrUX / GSC / GA4
./seo dataforseo <sub-cmd>   # live SEO data
./seo firecrawl <url>        # full-site crawl
./seo backlinks <url>        # free sources, opt-in premium
```

## Tip

Start with `./seo audit`, not single commands. Single commands optimise symptoms;
the broad pass shows the root cause. Then fix in dependency order — the
recommendation whose **Dependency** field points at another one is the one to do
first.
