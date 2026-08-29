# Contributing

Thank you for your interest in `seo-audit` — a self-contained, native port of
[claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT). Contributions are welcome.

## Getting started

```bash
cd seo-toolkit
./setup.sh      # installs workspace-local deps + Playwright Chromium
./seo doctor    # environment health check
```

## How to contribute

1. **Fork** the repository and work on a feature branch.
2. Follow the existing code style (Python, `lib/` modules, `scripts/`).
3. Keep the tool **self-contained and sandbox-safe**:
   - workspace-local `pylibs/` and `browsers/` (gitignored),
   - no global/system package installs,
   - pinned, known-good dependency versions.
4. Add or update tests where you change logic.
5. Open a **Pull Request** with a clear description.

## Commit messages

Use conventional commits (examples):
- `feat: add <feature>`
- `fix: <what broke>`
- `docs: <doc change>`
- `chore: <maintenance>`

## Reporting issues

Please include:
- A clear, concise title.
- Steps to reproduce.
- Expected vs. actual behavior.
- Your environment (macOS/Linux, Python version).

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE), consistent with the upstream `claude-seo` project.
