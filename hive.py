#!/usr/bin/env python3
"""
Hive CLI — skill pack manager and workspace setup.

Usage:
  uv run hive install google devops     # install packs
  uv run hive install --all             # install everything
  uv run hive remove marketing          # uninstall a pack
  uv run hive list                      # show available packs
  uv run hive setup                     # sync to workspace (symlinks + Cursor + MCP)
"""

import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

HIVE_DIR = Path(__file__).parent.resolve()
SKILLS_DIR = HIVE_DIR / "skills"
AVAILABLE_DIR = HIVE_DIR / "available"
PACKS_DIR = HIVE_DIR / "packs"
AGENTS_DIR = HIVE_DIR / "agents"
WORKSPACE_ROOT = HIVE_DIR.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def info(msg: str):
    print(f"[hive] {msg}")


def warn(msg: str):
    print(f"[hive] WARN: {msg}", file=sys.stderr)


def load_packs() -> dict:
    packs = {}
    for f in sorted(PACKS_DIR.glob("*.json")):
        with open(f) as fh:
            pack = json.load(fh)
            packs[pack["name"]] = pack
    return packs


def is_installed(skill: str) -> bool:
    return (SKILLS_DIR / skill).exists()


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

def install_local(pack: dict, force: bool = False) -> int:
    name = pack["name"]
    pack_dir = AVAILABLE_DIR / name

    if not pack_dir.exists():
        warn(f"available/{name}/ not found")
        return 1

    installed = 0
    for skill in pack["skills"]:
        src = pack_dir / skill
        dest = SKILLS_DIR / skill

        if dest.exists() and not force:
            print(f"  {skill}: already installed")
            continue
        if not src.exists():
            print(f"  {skill}: not found in available/{name}/")
            continue
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(src, dest)
        print(f"  {skill}: installed")
        installed += 1

    print(f"  {installed} skill(s) installed from {name}")
    return 0


def install_remote(pack: dict, force: bool = False) -> int:
    name = pack["name"]
    repo = pack["repo"]
    src_path = pack.get("path", "skills")

    print(f"  Cloning {repo}...")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", repo, tmp],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            warn(f"Clone failed: {e.stderr.decode().strip()}")
            return 1

        src_dir = Path(tmp) / src_path
        if not src_dir.exists():
            warn(f"Path '{src_path}' not found in repo")
            return 1

        installed = 0
        for skill in pack["skills"]:
            skill_src = src_dir / skill
            dest = SKILLS_DIR / skill

            if dest.exists() and not force:
                print(f"  {skill}: already installed")
                continue
            if not skill_src.exists():
                print(f"  {skill}: not found in repo")
                continue
            if dest.exists():
                shutil.rmtree(dest)

            shutil.copytree(skill_src, dest)
            print(f"  {skill}: installed")
            installed += 1

        print(f"  {installed} skill(s) installed from {name}")
        return 0


def install_pack(pack: dict, force: bool = False) -> int:
    name = pack["name"]
    source = pack.get("source", "local")

    if source == "builtin":
        print(f"\n[{name}] core — always installed")
        return 0

    lic = pack.get("license", "")
    print(f"\n[{name}] {pack['description']}")
    if lic:
        print(f"  License: {lic}")

    if source == "local":
        return install_local(pack, force)
    elif source == "github":
        return install_remote(pack, force)
    else:
        warn(f"Unknown source: {source}")
        return 1


# ---------------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------------

def remove_pack(pack: dict) -> int:
    name = pack["name"]
    if name == "core":
        warn("Cannot remove core pack")
        return 1

    removed = 0
    for skill in pack["skills"]:
        dest = SKILLS_DIR / skill
        if dest.exists():
            shutil.rmtree(dest)
            print(f"  {skill}: removed")
            removed += 1

    print(f"  {removed} skill(s) removed from {name}")
    return 0


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_packs(packs: dict):
    print("\nAvailable packs:\n")
    for name, pack in packs.items():
        source = pack.get("source", "local")
        skills = pack["skills"]
        installed = sum(1 for s in skills if is_installed(s))
        total = len(skills)

        if name == "core":
            status = "always installed"
        elif installed == total:
            status = "installed"
        elif installed > 0:
            status = f"partial ({installed}/{total})"
        else:
            status = "not installed"

        tag = ""
        if source == "github":
            repo_short = pack.get("repo", "").replace("https://github.com/", "").replace(".git", "")
            tag = f"  [github: {repo_short}]"

        print(f"  {name:20s} {total:2d} skills  {status}{tag}")
        print(f"  {'':20s} {pack['description']}")
        print()


# ---------------------------------------------------------------------------
# Setup (workspace symlinks + Cursor + MCP)
# ---------------------------------------------------------------------------

def backup_path(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = path.with_suffix(f".backup.{timestamp}{path.suffix}")
    shutil.move(str(path), str(backup))
    info(f"Backed up {path.name} -> {backup.name}")
    return backup


def create_symlink(target: Path, link_path: Path, label: str):
    link_path.parent.mkdir(parents=True, exist_ok=True)

    if link_path.is_symlink():
        current = link_path.resolve()
        if current == target.resolve():
            info(f"{label}: already linked")
            return
        backup_path(link_path)
    elif link_path.exists():
        backup_path(link_path)

    link_path.symlink_to(target)
    info(f"{label}: linked -> {target}")


def build_cursor_rules(skills_dir: Path, rules_dir: Path):
    rules_dir.mkdir(parents=True, exist_ok=True)
    for mdc in rules_dir.glob("*.mdc"):
        mdc.unlink()

    count = 0
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            skill_md = skill_path / "skill.md"
        if not skill_md.exists():
            continue
        shutil.copy(skill_md, rules_dir / f"{skill_path.name}.mdc")
        count += 1

    info(f"Cursor: {count} skills -> .mdc files")


def merge_mcp_configs(source: Path, target: Path):
    if not source.exists():
        return
    target_cfg = json.loads(target.read_text()) if target.exists() else {"mcpServers": {}}
    source_cfg = json.loads(source.read_text())

    added = []
    target_servers = target_cfg.setdefault("mcpServers", {})
    for name, server in source_cfg.get("mcpServers", {}).items():
        if name not in target_servers:
            target_servers[name] = server
            added.append(name)

    if added:
        target.write_text(json.dumps(target_cfg, indent=2) + "\n")
        info(f"MCP servers added: {', '.join(added)}")
    else:
        info("MCP: all servers already present")


def cmd_setup(args):
    info(f"Hive: {HIVE_DIR}")
    info(f"Workspace: {WORKSPACE_ROOT}")

    if not SKILLS_DIR.exists():
        warn(f"skills/ not found")
        return 1

    info("Actions:")
    print(f"  Symlink {WORKSPACE_ROOT}/.claude/skills -> {SKILLS_DIR}")
    print(f"  Symlink {WORKSPACE_ROOT}/.claude/agents -> {AGENTS_DIR}")
    print(f"  Generate .cursor/rules/ from skills")
    print(f"  Merge .mcp.json configs")
    print()

    if not args.yes:
        if not sys.stdin.isatty():
            warn("No TTY; use -y to skip confirmation")
            return 1
        reply = input("[hive] Proceed? [y/N]: ").strip().lower()
        if reply not in ("y", "yes"):
            info("Cancelled")
            return 1

    create_symlink(SKILLS_DIR, WORKSPACE_ROOT / ".claude" / "skills", "Claude skills")
    create_symlink(AGENTS_DIR, WORKSPACE_ROOT / ".claude" / "agents", "Claude agents")
    build_cursor_rules(SKILLS_DIR, WORKSPACE_ROOT / ".cursor" / "rules")

    hive_mcp = HIVE_DIR / ".mcp.json"
    workspace_mcp = WORKSPACE_ROOT / ".mcp.json"
    if hive_mcp.exists():
        merge_mcp_configs(hive_mcp, workspace_mcp)

    info("Done. Open Claude Code from workspace root to use hive skills.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(prog="hive", description="Hive CLI — skills, packs, workspace setup")
    sub = parser.add_subparsers(dest="command")

    # install
    p_install = sub.add_parser("install", help="Install skill packs")
    p_install.add_argument("packs", nargs="*", help="Pack names")
    p_install.add_argument("--all", action="store_true", help="Install all packs")
    p_install.add_argument("--force", action="store_true", help="Overwrite existing")

    # remove
    p_remove = sub.add_parser("remove", help="Remove a skill pack")
    p_remove.add_argument("pack", help="Pack name")

    # list
    sub.add_parser("list", help="List available packs")

    # setup
    p_setup = sub.add_parser("setup", help="Sync hive to workspace (symlinks + Cursor + MCP)")
    p_setup.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    args = parser.parse_args()
    packs = load_packs()

    if args.command == "list" or args.command is None:
        list_packs(packs)
        return 0

    elif args.command == "install":
        if not args.packs and not args.all:
            list_packs(packs)
            return 0
        targets = packs.keys() if args.all else args.packs
        for name in targets:
            if name not in packs:
                warn(f"Unknown pack: {name}")
                print(f"  Available: {', '.join(packs.keys())}")
                return 1
            result = install_pack(packs[name], args.force)
            if result != 0:
                return result
        return 0

    elif args.command == "remove":
        if args.pack not in packs:
            warn(f"Unknown pack: {args.pack}")
            return 1
        return remove_pack(packs[args.pack])

    elif args.command == "setup":
        return cmd_setup(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
