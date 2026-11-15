#!/usr/bin/env python3
"""Validate shared metadata and versions, and build client-specific plugin archives offline.

Run it from a checkout of the plugin repository (the main branch), or point --root at one.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

TARGETS = {
    "claude": [".claude-plugin/plugin.json", ".mcp.json"],
    "openai": ["plugin.json", "mcp.json"],
}
# Changing any of these changes what users install, so it needs a new plugin version.
PLUGIN_FILES = {"plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json", "mcp.json", ".mcp.json"}
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")


def read_json(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_key(version):
    match = SEMVER.fullmatch(version)
    require(match, f"Invalid version: {version}")
    major, minor, patch, prerelease = match.groups()
    # A prerelease sorts before the release with the same numbers.
    return int(major), int(minor), int(patch), prerelease is None, prerelease or ""


def find_skill_version(source):
    """Return `metadata.version` from SKILL.md frontmatter, or None when it is absent."""
    frontmatter = re.match(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)", source, re.S)
    if not frontmatter:
        return None
    block = re.search(r"^metadata:[ \t]*\r?\n((?:[ \t]+\S.*(?:\r?\n|$))+)", frontmatter.group(1), re.M)
    match = block and re.search(r'^[ \t]+version:[ \t]*"([^"]+)"[ \t]*$', block.group(1), re.M)
    return match.group(1) if match else None


def skill_version(skill):
    source = (skill / "SKILL.md").read_text(encoding="utf-8")
    # claude.ai rejects unknown top-level frontmatter keys, so the version lives under metadata.
    require(not re.search(r"^version:", source.split("\n---", 1)[0], re.M),
            f"{skill.name}: move the version under metadata")
    version = find_skill_version(source)
    require(version, f'{skill.name}: add metadata.version as a quoted string, e.g. version: "1.0.0"')
    version_key(version)
    return version


def check_skill_references(skill):
    """Require that every references/, scripts/, or examples/ path named in SKILL.md exists in the skill."""
    source = (skill / "SKILL.md").read_text(encoding="utf-8")
    for reference in sorted(set(re.findall(r"(?:references|scripts|examples)/[A-Za-z0-9._/-]*[A-Za-z0-9_-]", source))):
        target = skill / reference
        require(target.is_file() and target.resolve().is_relative_to(skill.resolve()),
                f"{skill.name}: SKILL.md refers to missing file {reference}")


def changelog_section(root, version):
    """Return the body of the `## [version] - YYYY-MM-DD` section in CHANGELOG.md, or None."""
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    pattern = rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}[ \t]*\r?\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.M | re.S)
    return match.group(1).strip() if match else None


def validate(root):
    canonical = read_json(root, "plugin.json")
    name, version = canonical["name"], canonical["version"]
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "Invalid plugin name")
    require(re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?", version), "Invalid version")
    claude = read_json(root, ".claude-plugin/plugin.json")
    gemini = read_json(root, "gemini-extension.json")
    for label, manifest in [("Claude", claude), ("Gemini", gemini)]:
        for field in ("name", "version", "description"):
            require(manifest.get(field) == canonical[field], f"{label} {field} differs from plugin.json")
    require(claude.get("license") == canonical.get("license"), "Claude license differs from plugin.json")

    portable_mcp = read_json(root, "mcp.json")["mcpServers"]
    claude_mcp = read_json(root, ".mcp.json")["mcpServers"]
    gemini_mcp = gemini["mcpServers"]
    for servers in (portable_mcp, claude_mcp, gemini_mcp):
        require(set(servers) == {name}, "Expected one MCP server matching the plugin name")
    endpoint = "https://mcp.dotidot.io/mcp"
    require(portable_mcp[name].get("type") == "streamable-http", "Invalid portable MCP transport")
    require(claude_mcp[name].get("type") == "http", "Invalid Claude MCP transport")
    require(portable_mcp[name].get("url") == endpoint, "Invalid portable MCP endpoint")
    require(claude_mcp[name].get("url") == endpoint, "Invalid Claude MCP endpoint")
    require(gemini_mcp[name].get("httpUrl") == endpoint, "Invalid Gemini MCP endpoint")

    for manifest_path, source in [
        (".claude-plugin/marketplace.json", "./"),
        (".agents/plugins/marketplace.json", {"source": "local", "path": "./"}),
    ]:
        marketplace = read_json(root, manifest_path)
        require(marketplace["name"] == name, f"Unexpected marketplace name in {manifest_path}")
        entries = marketplace["plugins"]
        require(len(entries) == 1 and entries[0]["name"] == name, f"Unexpected plugin in {manifest_path}")
        require(entries[0]["source"] == source, f"Unexpected source in {manifest_path}")

    skills_root = root / "skills"
    require(skills_root.is_dir() and not skills_root.is_symlink(), "Missing or linked skills directory")
    skills = sorted(path for path in skills_root.iterdir() if not path.name.startswith("."))
    require(bool(skills), "No skills found")
    for skill in skills:
        require(skill.is_dir() and (skill / "SKILL.md").is_file(), f"Missing SKILL.md: {skill.name}")
    skill_versions = {skill.name: skill_version(skill) for skill in skills}
    for skill in skills:
        check_skill_references(skill)
    require(changelog_section(root, version) is not None,
            f"CHANGELOG.md needs a '## [{version}] - YYYY-MM-DD' section for the current plugin version")
    return name, version, skill_versions


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


def file_at(root, revision, path):
    result = subprocess.run(["git", "show", f"{revision}:{path}"], cwd=root, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def check_versions_against(root, ref, version, skill_versions):
    """Require raised versions for every plugin and skill change since the merge base with `ref`."""
    base = git(root, "merge-base", ref, "HEAD").strip()
    changed = set(git(root, "diff", "--name-only", base).splitlines())
    changed |= set(git(root, "ls-files", "--others", "--exclude-standard").splitlines())
    base_manifest = file_at(root, base, "plugin.json")
    if base_manifest is None:
        print(f"No plugin.json at {ref}; skipping the version comparison")
        return
    base_version = json.loads(base_manifest)["version"]
    problems = []
    if version_key(version) < version_key(base_version):
        problems.append(f"plugin version {version} is lower than {base_version} on {ref}")
    content = sorted(path for path in changed if path.startswith("skills/") or path in PLUGIN_FILES)
    if content and version_key(version) <= version_key(base_version):
        problems.append(f"plugin content changed ({', '.join(content)}); raise the version in plugin.json above {base_version}")

    released = []
    for skill, current in skill_versions.items():
        prefix = f"skills/{skill}/"
        base_source = file_at(root, base, f"{prefix}SKILL.md")
        previous = find_skill_version(base_source) if base_source else None
        if previous is not None and version_key(current) < version_key(previous):
            problems.append(f"skill {skill} version {current} is lower than {previous} on {ref}")
        elif previous is not None and current == previous and any(path.startswith(prefix) for path in changed):
            problems.append(f"skill {skill} changed; raise its metadata.version above {previous}")
        if current != previous:
            released.append(f"`{skill}` {current}")

    if version != base_version:
        section = changelog_section(root, version) or ""
        problems += [f"the CHANGELOG {version} section must mention {entry}" for entry in released if entry not in section]
    require(not problems, f"Version check against {ref} failed:\n- " + "\n- ".join(problems))
    summary = ", ".join(released) or "no skill version changes"
    print(f"Versions checked against {ref}: plugin {base_version} -> {version}; {summary}")


def package_files(root):
    shared = [Path("README.md"), Path("docs/testing.md")]
    if (root / "LICENSE").exists():
        shared.append(Path("LICENSE"))
    for path in sorted((root / "skills").rglob("*")):
        relative = path.relative_to(root)
        require(not path.is_symlink(), f"Symlinks cannot be packaged: {relative}")
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        if path.is_file() and path.suffix != ".pyc":
            shared.append(relative)
    # Ship every file in .claude-plugin/ except the marketplace, so the archive carries the
    # directory icon without any script or manifest naming the image: the directory holds
    # plugins whose code can reach a bundled image.
    claude_dir = [path.relative_to(root).as_posix() for path in sorted((root / ".claude-plugin").iterdir())
                  if path.is_file() and path.name not in {"marketplace.json", ".DS_Store"}]
    extra = {"claude": claude_dir}
    packages = {}
    for target, manifests in TARGETS.items():
        paths = sorted(set(shared + [Path(path) for path in manifests + extra.get(target, [])]))
        for path in paths:
            absolute = root / path
            require(absolute.is_file() and not absolute.is_symlink(), f"Missing or linked file: {path}")
            require(absolute.resolve().is_relative_to(root.resolve()), f"File outside repository: {path}")
        packages[target] = paths
    return packages


def build(root, check_only=False, against=None):
    name, version, skill_versions = validate(root)
    if against:
        check_versions_against(root, against, version, skill_versions)
    packages = package_files(root)
    if check_only:
        print(f"Package inputs valid: {name} {version} ({len(packages)} targets)")
        return
    output = root / "dist"
    output.mkdir(exist_ok=True)
    checksums = []
    for target, files in packages.items():
        archive = output / f"{name}-{target}-{version}.zip"
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
            for path in files:
                source = root / path
                entry = ZipInfo(path.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.compress_type = ZIP_DEFLATED
                permissions = 0o100755 if source.stat().st_mode & 0o111 else 0o100644
                entry.external_attr = permissions << 16
                package.writestr(entry, source.read_bytes())
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        checksums.append(f"{checksum}  {archive.name}\n")
        print(f"Built {archive.relative_to(root)} ({len(files)} files)")
    (output / "SHA256SUMS").write_text("".join(checksums), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs without writing archives")
    parser.add_argument("--against", metavar="REF",
                        help="Also require raised plugin and skill versions for changes since this Git ref, e.g. origin/main")
    parser.add_argument("--notes", action="store_true",
                        help="Print the CHANGELOG section of the current plugin version and exit")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="The plugin repository to check and package (default: the current directory)")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.notes:
            _, version, _ = validate(root)
            print(changelog_section(root, version))
            return 0
        build(root, check_only=args.check, against=args.against)
    except subprocess.CalledProcessError as error:
        print(f"Packaging failed: git {' '.join(error.cmd[1:])}: {error.stderr.strip()}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
