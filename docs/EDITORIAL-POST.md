# seo-audit — editorial guest-post template (Medium / Dev.to / Hacker News)

A value-first, redactional post you can publish on a third-party platform to earn a
genuine backlink to https://github.com/Haniubub/seo-toolkit. It answers a real question
(how to run a serious SEO audit inside DeepSeek Harness) rather than selling a tool.
Keep the brackets as your personal framing. Do not claim "best" or "only" — say what is
demonstrably true and defensible.

---

## Title options

- "How to run a full, weighted SEO audit inside DeepSeek Harness"
- "SEO audits were Claude-Code-bound. Here's how to run one natively in DeepSeek Harness"
- "A practical DSH-native SEO audit: 53 scripts + LLM judgment, no SaaS"

## Body

### The setup

If you work in DeepSeek Harness (DSH), you know the plugin ecosystem is rich, but a
*complete* SEO audit skill is the thing that was usually missing. Most serious SEO audit
skills are built for Claude Code, which means leaving your environment or making do with
a partial check. seo-audit closes that gap: a full, weighted audit that runs natively in
DSH, entirely on your machine.

### What it does

It splits the work cleanly. The **measurement** layer is deterministic — 53 Python
scripts plus a `lib/` core, run via `./seo <command>`. The **judgment** layer is
LLM-driven — 24 sub-skills and 18 specialist agents for E-E-A-T, GEO/AI Overviews,
Local/GBP, SXO, schema, and more. Everything is synthesised into one weighted score:
Technical 22% · Content 23% · On-Page 20% · Schema 10% · Performance 10% ·
AI-Readiness 10% · Images 5%.

### Run it

```bash
git clone https://github.com/Haniubub/seo-toolkit.git
cd seo-toolkit
./setup.sh
./seo audit https://example.com
```

`./seo audit` detects the business type, then fans out to only the relevant sub-agents
in parallel (never all 18), and merges the results into one prioritised action plan.
Every recommendation ships with the four claude-seo fields: Observation → Dependency →
Failure signal → Early indicator — so you know whether a fix actually worked.

### Why it's worth a look

- **DSH-native** — runs in the harness you already use, no Claude Code required.
- **No API key** for the core audit; the measurement layer is pure local Python.
- **No SaaS, no per-domain pricing** — nothing leaves your machine.
- **Grounded in Google's primary sources**, not blog folklore.

### The honest note

This isn't the only SEO tool, and it isn't claiming to be the best. What it is: the first
complete SEO audit toolkit I've seen that runs natively in DeepSeek Harness, without
Claude Code, and with the measurement layer free. If that describes what you need, it's
worth 10 minutes.

_Repo: [Haniubub/seo-toolkit](https://github.com/Haniubub/seo-toolkit)_

---

## Platform notes

- **Medium / Dev.to:** publish as-is, add tags (`DeepSeek`, `SEO`, `AI`, `harness`).
  Keep the code block; add a short TL;DR line at the top.
- **Hacker News:** post the title + a 1–2 sentence summary as the text, link the repo.
  Do not paste the full body. Be ready for technical questions — this audience checks claims.
