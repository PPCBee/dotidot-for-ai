# Working on the Dotidot plugin

This repository is public. Everything committed here, including history, reaches customers and other companies.

- Keep reusable workflows in `skills/<name>/SKILL.md`, shared across clients. Write skill instructions in English and have skills answer in the user's language. Follow `docs/skill-guidelines.md` when creating or changing a skill.
- `plugin.json` is the canonical plugin identity and version. Keep `.claude-plugin/plugin.json` and `gemini-extension.json` consistent with it.
- The remote MCP endpoint is `https://mcp.dotidot.io/mcp`. Portable `mcp.json` uses `streamable-http`, Claude `.mcp.json` uses `http`, and Gemini uses `httpUrl`. These are intentionally different client formats.
- Authenticate through the client's OAuth flow. Never add tokens, passwords, client secrets, customer data, internal notes, or customer identifiers from test runs to this repository or its release archives.
- Verify tool capabilities against the live tool schemas after authentication. Do not invent tool parameters or copy a full tool catalog into skills.
- Keep diagnostic skills read-only. A skill that writes to an account follows "Skills that change an account" in `docs/skill-guidelines.md`.
- Verification against a real account is read-only. Do not invoke write tools while testing.
- Version every plugin change: when a skill changes, raise its `metadata.version` in `SKILL.md` and the plugin version in `plugin.json` and its mirrors, and add a `## [x.y.z] - YYYY-MM-DD` changelog section naming each changed skill as `` `name` x.y.z``. Verify with `python3 scripts/package.py --check --against origin/main`. Merging a new plugin version into `main` publishes its tag and GitHub release.
- Run `claude plugin validate .` when Claude Code is available, and the smoke scenarios in `docs/testing.md` after changing skill behavior.
- In installation instructions, keep the verification status truthful and distinguish connecting the MCP server from installing the skills.
- Use feature branches. Do not commit, push, publish, or choose a license unless requested.
