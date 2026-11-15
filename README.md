# CI tools for the Dotidot plugin

This branch holds the tooling that checks and packages the Dotidot plugin. The plugin itself lives on `main`. The tooling is kept here, outside the plugin, because Anthropic's plugin directory scans every file on `main` and accepts scripts only from verified organizations.

`scripts/package.py` validates the shared metadata, requires raised plugin and skill versions for every change, and builds the client-specific ZIP archives.

## Use

The workflow on `main` checks out this branch at a pinned tag (`ci-tools-v<n>`) into `.tools/` and runs the script against the repository. To run it locally from a checkout of `main`:

```sh
git worktree add ../dotidot-ci-tools ci-tools
python3 ../dotidot-ci-tools/scripts/package.py --check --against origin/main
python3 ../dotidot-ci-tools/scripts/package.py          # builds dist/
```

`--root` points the script at another checkout; it defaults to the current directory.

## Release a change

1. Open a pull request into `ci-tools`.
2. After the merge, tag the new commit as the next `ci-tools-v<n>` and push the tag.
3. On `main`, raise the pinned tag in `.github/workflows/package.yml` in a pull request; its checks run the new version.
