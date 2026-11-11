---
title: Contributing
---

## Contributing

Contributions are welcome! Here's how you can help.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/jr2804/teddi-tool.git
cd teddi-tool

# Install the pinned tool versions (node, bun, ruff, ty, rumdl, pyreorder, ...)
# then sync the dev dependencies declared in pyproject.toml.
# (mise install is the mise command that installs the tool versions in
# .config/mise/config.toml; it is NOT a task — `mise dev` is the task that
# syncs Python dev deps.)
mise install
uv sync --dev
# or: mise dev    # composite task that runs `uv sync -U --dev --all-extras --all-groups`
```

### Running Tests

```bash
mise test          # pytest with coverage
```

### Code Quality

```bash
# The single command a contributor should run before opening a PR:
mise all           # runs test, lint, spell, format, format-md, docs

# Individual steps (use these while iterating):
mise lint          # ruff check --fix
mise spell         # codespell
mise typecheck     # static type check (ty)
mise format        # ruff format + ruff check --select I + pyreorder run
mise format-md     # rumdl over Markdown
mise docs          # build the Zensical documentation
```

`mise all` covers style and documentation, but not static typing; run
`mise typecheck` as well before opening a pull request (CI runs it separately).

See the [Development guide](development.md) for architecture notes and the
release process.

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
