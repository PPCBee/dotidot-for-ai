# Verification

## Static checks

From the repository root, with the `ci-tools` branch checked out next to it (`git worktree add ../dotidot-ci-tools ci-tools`):

```sh
python3 ../dotidot-ci-tools/scripts/package.py --check --against origin/main
claude plugin validate .
python3 ../dotidot-ci-tools/scripts/package.py
```

The first command checks that all manifests share the name, version, description, and MCP endpoint, that every skill has a `metadata.version`, and that changed skills and manifests come with raised versions and a changelog section. The last command builds the archives in `dist/`; check that they contain only the manifests, `README.md`, `docs/testing.md`, and `skills/`.

## Installation checks

Record the client and its version, the installation route, and the result. A schema check or successful OAuth discovery is not a passed installation.

| Route | Expected result |
| --- | --- |
| Organization sync | The marketplace syncs without errors, `dotidot` appears in **Inventory** with the plugin version, and its **Connectors & tools** lists Dotidot. |
| Member in claude.ai | The plugin appears under **Customize > Plugins** with the chosen availability, `check-permissions` is listed on its **Skills** tab, and the **Connectors** tab shows Dotidot as Connected after sign-in. |
| Claude Code | `/plugin` lists `dotidot`, `/mcp` lists the `dotidot` server, and sign-in completes. |
| Update | After a release with a higher version, the new version reaches members without reinstalling. |

## Smoke scenarios

Run these with a Dotidot account that is allowed to be used for testing. Inspect the tool calls as well as the answer. These scenarios only read data.

| Scenario | Expected behavior |
| --- | --- |
| "Which Dotidot organizations can I access?" | Calls `whoami` and `list_organizations`, then reports the account and a table of organizations with access levels. |
| "What can I do in <organization>?" with one matching organization | Checks only that organization with `list_organization_members` and explains the access level. |
| An account with more than five organizations | Lists them all, checks none or at most five, and asks which to check. |
| The Dotidot demo organization, or one whose members are not readable | Reports the level as not determined with the reason; does not guess. |
| "Who else is in <organization>?" not asked | Does not list other members' names or emails. |
| "Make me a full member" or "Invite a colleague" during the check | Does not call write tools; treats it as a separate request. |
| "Which ad accounts are linked to <organization>?" | Does not answer from this skill; linked accounts are a different topic. |
| Not connected to Dotidot | Explains how to connect `https://mcp.dotidot.io/mcp`; in claude.ai, points to the plugin's **Connectors** tab and says that **Not added** needs an organization Owner to add the connector; does not ask for a password or API key and does not claim to have read data. |
| Any completed answer | Has the Account, Organizations, and Not checked parts in the user's language. |

Keep customer names, IDs, and results out of this repository.
