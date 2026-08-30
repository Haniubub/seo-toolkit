# seo-audit — share snippet

Copy-paste this wherever you'd tell people about it. It's written to earn a
repost, not to sell a hard pitch.

---

## The punchy pitch

> **A complete, weighted SEO audit for ~4 cents.**
> Deterministic measurement (53 scripts) + LLM judgment, Google-aligned scoring,
> no SaaS, runs locally. **12–30× cheaper than the Claude equivalent — and the
> quality actually holds up.** This is a quality-per-dollar gap that didn't exist
> before.

---

## The longer version (for a post/comment)

**Run a full, weighted SEO audit for the price of a few cents.**

`seo-audit` is a local, fully self-contained audit toolkit for DeepSeek Harness.
Point it at any URL and it measures **technical SEO, on-page, schema.org/JSON-LD,
local/GBP, Core Web Vitals, GEO/AI-Overview readiness, content/E-E-A-T, sitemap,
hreflang and more** with a deterministic Python CLI, then synthesises everything
into one weighted, prioritised report grounded in Google's primary sources.

- **Quality you couldn't get at this price before.** 7 weighted categories
  (Technical 22% · Content/E-E-A-T 23% · On-Page 20% · Schema 10% · Performance
  10% · AI-Readiness 10% · Images 5%), 53 deterministic measurement scripts, and
  Google Search Essentials / helpful-content / Core Web Vitals / AI Optimization
  guidance — not blog-level folklore.
- **~$0.04 per audit.** The measurement layer is pure local Python (**$0 in LLM
  tokens**); only the LLM judgment costs anything. The same audit on Claude runs
  **~$0.45–$1.13** — that's **12–30×** more.
- **Local-first, no SaaS.** No plugin marketplace, no per-domain pricing, nothing
  leaves your machine.
- **Gated multi-agent fan-out.** It detects the industry and only spawns the
  agents you actually need — never all 18.

Install it in 3 steps, then:

```bash
./seo audit https://example.com
```

Free, open, and it runs where you already work.

---

### One-liners

- "A complete, weighted SEO audit for ~4 cents. This quality-per-dollar gap didn't exist before."
- "SEO audit = $0.04 × full weighted quality. 12–30× cheaper than Claude."
- "No SaaS, no per-site pricing. Just `./seo audit <url>` — and it's actually good."
