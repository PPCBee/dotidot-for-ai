# Contributing a skill

This is the process for adding or changing a skill that Dotidot customers get through the plugin. It is written for Claude Code working with a Dotidot colleague who may not be a developer: the colleague describes what customers need and checks the results, and Claude does the repository work, from the skill itself to the pull request.

Every pull request needs a code owner's approval (see `.github/CODEOWNERS`) before it can merge into `main`, and only a merge releases anything. Opening a pull request never reaches customers.

## Working with the colleague

- Talk in the colleague's language, briefly and without jargon. Do not show file names, branches, or commands unless they ask; that is your part of the work.
- Ask several questions at once rather than one by one, and offer choices where the client lets you.
- Keep the colleague informed at each step below in one or two sentences.

## 0. Before starting

Check these yourself and fix or explain what is missing:

- The working tree is clean and `main` is up to date with `origin/main`.
- The `ci-tools` branch is checked out next to the repository: `git worktree add ../dotidot-ci-tools ci-tools` if `../dotidot-ci-tools` is missing.
- The Dotidot connector is available: call `whoami`. If the tools are missing or sign-in fails, ask the colleague to connect `https://mcp.dotidot.io/mcp` (in Claude Code: `/mcp`, select `dotidot`, sign in) and wait.
- The colleague can push to the repository. If a push is refused, tell them to ask the code owner for access.

## 1. Understand the request

Ask, all at once:

1. **What should customers be able to do?** The problem or task, and who does it (for example a PPC specialist or an e-shop owner).
2. **How would they ask?** Two or three example prompts, in the words a customer would use.
3. **Read only, or changes to the account?** Read only is the default. A skill that changes an account follows "Skills that change an account" in `docs/skill-guidelines.md` and gets a stricter review.
4. **What does a good answer look like?** What it must contain, and what would make it useless.

Then read `skills/`. If an existing skill covers most of the request, propose extending it instead of adding a new one, and say why.

## 2. Check what the Dotidot tools can do

Read the live tool list and descriptions of the Dotidot connector. Choose the tools the skill needs, and for a read-only skill confirm that each one only reads (its annotations or description say so). If the tools cannot provide what the request needs, tell the colleague what is missing and agree on a narrower skill or stop. Never invent tools or parameters, and do not copy the tool catalog into the skill.

## 3. Write the skill

- Create a branch `feature/skill-<name>` for a new skill or `fix/skill-<name>` for a change.
- Follow `docs/skill-guidelines.md`: naming, frontmatter, the safety rules, evidence and output, fixed answer structures in `references/`, instructions in English with answers in the user's language.
- Do not add scripts or other executable files, and do not send data anywhere but the Dotidot MCP server (see "Data destinations" in `docs/skill-guidelines.md`).
- Update the table in "What it contains" in `README.md` and add smoke scenarios for the skill to `docs/testing.md`.
- Do not change manifests other than their versions, `.mcp.json`, workflows, `CODEOWNERS`, or the `ci-tools` branch as part of a skill. Those changes go in a separate pull request that the colleague asks for explicitly.

## 4. Raise the versions

Follow "Versions and releases" in `README.md`: give a new skill `metadata.version: "0.1.0"` or raise a changed skill's version, raise the plugin version in `plugin.json`, `.claude-plugin/plugin.json`, and `gemini-extension.json`, and add the `CHANGELOG.md` section naming the skill and its version. If another pull request takes the same plugin version first, update the branch from `main` and raise the version again.

## 5. Test

- Run `python3 ../dotidot-ci-tools/scripts/package.py --check --against origin/main` and `claude plugin validate .`, and fix every finding.
- Load the plugin from the working tree in a new Claude Code session (`claude --plugin-dir .`) and run each example prompt, plus the new smoke scenarios, against the Dotidot demo organization or a test organization the colleague names. Inspect the tool calls as well as the answers.
- Test read-only. Never call write tools on a customer's account. A skill that changes an account is tested only in a test organization the colleague confirms is meant for it, and only after they agree to each change.
- Show the colleague the answers and adjust the skill until they are satisfied.

## 6. Open the pull request

- Commit in English, in the imperative mood, and push the branch.
- Open a pull request into `main` that fills in `.github/pull_request_template.md`, in Czech. Describe the test runs without customer names, IDs, or data.
- Do not merge it, push to `main`, or approve it. The code owner reviews it.
- Send the colleague the pull request link and explain what happens next: the code owner reviews it, possibly with comments to address in the same branch, and after the merge the plugin is released and Anthropic's directory checks the new version before customers get it.

## After the review

Address each review comment in the same branch, reply in its thread with what changed and in which commit, or why it was not changed, and resolve the thread. Run the checks in step 5 again after each change.

## What happens after the merge

The workflow on `main` creates the `v<version>` tag and GitHub release. The Claude directory picks up the new commit, runs its validation and security scan, and publishes the version, automatically or after an Anthropic reviewer approves it. Customers who installed the plugin then get the update without reinstalling it.
