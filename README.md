# Dotidot for AI

The Dotidot plugin connects your AI assistant to your Dotidot account and adds Dotidot skills: instructions that tell the assistant how to work with your feeds, data sources, and organizations. It is built for Claude and also packaged for other clients that support Agent Skills and MCP.

Status: early preview. The plugin contains one skill, `check-permissions`, which confirms the connection works.

## What it contains

| Part | What it does |
| --- | --- |
| Dotidot connection | Connects to the Dotidot MCP server at `https://mcp.dotidot.io/mcp`. You sign in with your own Dotidot account through OAuth; no API key is needed. The assistant gets exactly your Dotidot permissions. |
| `check-permissions` skill | Shows which Dotidot account the assistant is connected as, which organizations it can reach, and your permissions in each. It only reads. Try: "Which Dotidot organizations can I access, and what can I do there?" |

Installing the plugin does not sign you in. Connect Dotidot once, as described below, and the skills can then read your data.

## Install in Claude

### For your whole organization (Team and Enterprise)

An Owner sets up Dotidot once from Anthropic's plugin directory, and members get it in claude.ai, the desktop app, Cowork, and Claude Code:

1. In claude.ai, open **Organization settings > Plugins & skills**, find Dotidot on the **Inventory** tab, open its menu, and select **Default access**: **Available to install**, **Installed by default**, or **Required**. Dotidot appears there only while your organization keeps Anthropic's directory as a source.
2. Open **Organization settings > Connectors** and add the Dotidot connector with the URL `https://mcp.dotidot.io/mcp`. A plugin's availability setting does not add its connector.
3. Each member connects Dotidot with their own account, from the plugin's **Connectors** tab in **Customize > Plugins**.

Until Dotidot is listed in the directory, members install it themselves as described below. See [Manage plugins for your organization](https://claude.com/docs/plugins/admin.md).

### For yourself

In claude.ai or the desktop app, open **Customize > Plugins**:

- **Discover**: find Dotidot in the directory and select **Add**.
- Or **Add > Add marketplace** and enter `PPCBee/dotidot-for-ai`. For a private repository, connect GitHub and give the Claude GitHub App access when asked.
- Or **Add > Upload plugin** with `dotidot-claude-<version>.zip` from the [latest release](https://github.com/PPCBee/dotidot-for-ai/releases/latest).

Then open the plugin's **Connectors** tab and connect Dotidot. The plugin installs even when the connector is missing, so check this tab. If it shows **Not added** and you can't add it yourself, ask an Owner of your organization to add the Dotidot connector in **Organization settings > Connectors**, then connect it with your own account.

### Claude Code

```text
/plugin marketplace add PPCBee/dotidot-for-ai
/plugin install dotidot@dotidot
```

Run `/mcp`, select `dotidot`, and sign in. Plugins installed in claude.ai also reach Claude Code sessions signed in to the same account. For a private repository, Claude Code uses your local Git credentials.

### Connector only

The Add to Claude button on [dotidot.io](https://www.dotidot.io/product/mcp) adds the Dotidot connector without the skills.

## Other clients

The same skills and connection are packaged for other clients. These installations have not yet been verified against Dotidot sign-in.

- **Codex:** in a version with plugin marketplaces, run `codex plugin marketplace add` with the path to a clone of this repository, then `codex plugin add dotidot@dotidot`.
- **Gemini CLI:** `gemini extensions install https://github.com/PPCBee/dotidot-for-ai`, then `/mcp auth dotidot`.
- **ChatGPT:** add a custom MCP server with the endpoint above. This connects your data without the skills.

## Privacy and permissions

The plugin contains no credentials and stores no data. Requests go from your AI client directly to the Dotidot MCP server, which applies your Dotidot account's permissions. Skills that only read say so, and a skill that changes data will describe each change and ask for your confirmation first. Your AI client may also ask before each change.

## Development

| Path | Purpose |
| --- | --- |
| `skills/` | Skills shared by all clients. Rules: [skill guidelines](docs/skill-guidelines.md); adding one with Claude Code: [contributing a skill](docs/contributing-skills.md). |
| `.claude-plugin/` | Claude plugin manifest, marketplace, and the directory icon, which the directory finds here by its standard name. |
| `.mcp.json` | Claude MCP connection. |
| `plugin.json`, `mcp.json` | Portable Agent Plugins manifests for OpenAI-compatible clients. |
| `.agents/plugins/marketplace.json` | Codex marketplace. |
| `gemini-extension.json` | Gemini CLI extension. |
| `ci-tools` branch | `scripts/package.py`: metadata and version checks, and reproducible ZIP builds. It lives outside the plugin because the Claude directory accepts scripts in a plugin only from verified organizations. |
| `.github/workflows/package.yml` | Checks pull requests, builds packages, and publishes a release for each new version. |
| `docs/testing.md` | Static checks and smoke scenarios. |
| `CHANGELOG.md` | Releases and the skill versions they contain. |
| `AGENTS.md`, `CLAUDE.md` | Instructions for AI agents working in this repository. |
| `.github/CODEOWNERS`, `.github/pull_request_template.md` | The code owner who approves every change, and the pull request template. |
| `LICENSE` | MIT license. |

### Versions and releases

The plugin and each skill have their own [semantic version](https://semver.org):

- **Plugin:** `version` in `plugin.json`, mirrored in `.claude-plugin/plugin.json` and `gemini-extension.json`. Raise it for every change to skills or manifests; clients do not deliver changes while the version stays the same.
- **Skill:** `metadata.version` in the skill's `SKILL.md` frontmatter, as a quoted string. Raise the major version for changed behavior or a new account write, the minor version for a new scenario, and the patch version for a wording fix. While the major version is 0, raise the minor version for changed behavior.
- **Changelog:** a `## [x.y.z] - YYYY-MM-DD` section for each plugin version that names every changed skill with its new version.

Before opening a pull request, check out the `ci-tools` branch next to the repository once, then run the checks from the repository root:

```sh
git worktree add ../dotidot-ci-tools ci-tools   # once
python3 ../dotidot-ci-tools/scripts/package.py --check --against origin/main
claude plugin validate .
```

Pull requests run the same version check. After a merge to `main` with a new plugin version, the workflow creates the `v<version>` tag and a GitHub release with `dotidot-claude-<version>.zip`, `dotidot-openai-<version>.zip`, and `SHA256SUMS`. `python3 ../dotidot-ci-tools/scripts/package.py` builds the same archives locally in `dist/`. The workflow runs the `ci-tools` branch at the tag pinned in `CI_TOOLS_REF`; see the README on that branch for changing the tooling.
