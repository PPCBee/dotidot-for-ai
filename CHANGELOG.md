# Changelog

Notable changes to the Dotidot plugin, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Each release is headed by the plugin version and date, such as `## [0.1.0] - 2026-11-14`, and names each skill whose version changed, such as `check-permissions` 0.1.0.

## [0.1.4] - 2026-11-15

### Changed

- The Claude manifest names the icon again, so the directory shows it.
- The packaging and version checks moved out of the plugin to the `ci-tools` branch; installs no longer include them.

## [0.1.3] - 2026-11-15

### Changed

- No changes to the skills or the connection. This release resubmits the plugin to the directory after the publishing organization was verified, and adds guidance for skill authors on where skills may send data.

## [0.1.2] - 2026-11-15

### Changed

- The Claude manifest no longer names the icon file; the directory finds the icon at its standard location, `.claude-plugin/`.

## [0.1.1] - 2026-11-15

### Changed

- Re-encoded the directory icon without changing how it looks, so the directory's file checks no longer flag it.

## [0.1.0] - 2026-11-14

### Added

- The Dotidot plugin with a connection to the Dotidot MCP server at `https://mcp.dotidot.io/mcp`. You sign in with your own Dotidot account; no API key is needed.
- `check-permissions` 0.1.0: shows which Dotidot account the assistant is connected as, which organizations it can reach, and your permissions in each. It only reads.
