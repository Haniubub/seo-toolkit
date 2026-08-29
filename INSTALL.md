# seo-audit — install in 3 steps

Drop `seo-audit` into your DeepSeek Harness skills directory and you have a full
local & technical SEO audit engine. No SaaS, no per-domain pricing, no third
party — the measurement layer runs on your machine.

## 1. Get the toolkit

Clone the repo, then run the single setup command. It installs the pinned Python
dependencies into a workspace-local `pylibs/` and Playwright Chromium into
`browsers/` — nothing touches your global Python or system.

```bash
git clone https://github.com/Haniubub/seo-toolkit.git
cd seo-toolkit
./setup.sh            # one command: pylibs/ + Chromium + smoke test
```

The version-pinned dependencies (`requirements.txt`) are installed with
`pip install --target pylibs`, so the toolkit is fully self-contained — it does
not depend on packages being installed globally.

## 2. Point the skill at it

The skill looks for the toolkit in a few places, in order:

1. `$SEO_TOOLKIT` — set this and you're done
2. The `seo-toolkit/` folder beside this skill
3. `./seo` on `PATH`

## 3. Copy the skill into DSH

```bash
mkdir -p ~/.dsh/skills/seo-audit
cp SKILL.md ~/.dsh/skills/seo-audit/
```

Then in a DSH session, verify it works:

```bash
./seo doctor                  # sanity check — expect "Playwright-Chromium: OK"
./seo audit https://example.com   # full weighted audit
```

> **Note:** the first `./seo doctor` may occasionally time out under the sandbox
> because it launches a headless Chromium. Just retry — it is a transient launch
> flake, not a broken install.

That's it. The skill triggers automatically whenever you ask to audit or improve
a website's search visibility.
