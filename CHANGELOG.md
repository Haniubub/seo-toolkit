# Changelog

All notable changes to this project are documented here.

## v1.0.0 — 2026-08-29
- Initial release: native, self-contained port of `claude-seo` v2.2.5
  (measurement engine + LLM judgment for local/technical SEO).
- Weighted SEO Health Score (Technical 22% · Content 23% · On-Page 20% ·
  Schema 10% · Performance 10% · AI-Readiness 10% · Images 5%).
- Gated multi-agent fan-out (`audit-fanout.workflow.js`) with industry &
  credential gating.
- Sandbox-safe runtime: workspace-local `pylibs/` and `browsers/`.
- Professional English README, MIT license, CI workflow.
- Repo hygiene: `.gitignore`, de-duplication, removal of regenerable artifacts.
