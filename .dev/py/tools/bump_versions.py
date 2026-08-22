import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent.parent
PY_DIR = SCRIPT_DIR.parent
UTILS_DIR = PY_DIR / "utils"

sys.path.insert(0, str(DEV_DIR))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(UTILS_DIR))

from registry import VERSIONS
from logger import ConsoleLogger
from git import run_git
from update_changelog import get_base_branch, get_commits, get_component_path_by_scope

REGISTRY_PATH = DEV_DIR / "registry.py"

BUMP_RANK = {"patch": 1, "minor": 2, "major": 3}

HEADER_PATTERN = re.compile(r"^(feat|fix|refactor|perf)\(([^)]+)\)(!?):\s*(.+)$", re.MULTILINE)
VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def get_root_dir() -> Path:
    return SCRIPT_DIR.parent.parent.parent


def has_unreleased_section(root: Path, comp_path: str) -> bool:
    """A component only needs a bump while its changelog still has an
    [Unreleased] section. After apply_versions.py promotes it, re-running
    this tool must not bump the same component twice (idempotency guard)."""
    changelog = root / comp_path / "CHANGELOG.md"
    if not changelog.exists():
        return False
    content = changelog.read_text(encoding="utf-8")
    return bool(re.search(r"^## \[Unreleased\]", content, re.MULTILINE | re.IGNORECASE))


def bump_for_header(commit_type: str, bang: str, full_message: str) -> str:
    if bang == "!" or "BREAKING CHANGE" in full_message:
        return "major"
    if commit_type == "feat":
        return "minor"
    return "patch"


def next_version(current: str, bump: str) -> str:
    m = VERSION_PATTERN.match(current)
    if not m:
        return ""
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def collect_bumps(root: Path, commits: list[list[str]]) -> dict[str, str]:
    bumps: dict[str, str] = {}
    for commit_hash, _subject in commits:
        message = run_git(["show", "-s", "--format=%B", commit_hash], root)
        for commit_type, scope, bang, _msg in HEADER_PATTERN.findall(message):
            comp_path = get_component_path_by_scope(scope)
            if not comp_path:
                continue
            bump = bump_for_header(commit_type, bang, message)
            current = bumps.get(comp_path)
            if current is None or BUMP_RANK[bump] > BUMP_RANK[current]:
                bumps[comp_path] = bump
    return bumps


def apply_to_registry(new_versions: dict[str, str]) -> None:
    content = REGISTRY_PATH.read_text(encoding="utf-8")
    for comp_path, version in new_versions.items():
        content = re.sub(
            rf'("{re.escape(comp_path)}"\s*:\s*")[^"]+(")',
            rf"\g<1>{version}\g<2>",
            content,
            count=1,
        )
    REGISTRY_PATH.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Bump component versions in .dev/registry.py based on branch commit labels."
    )
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Apply the bumps without the interactive confirmation (for CI or scripted use)")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would change")
    args = parser.parse_args()

    root = get_root_dir()
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    if not branch:
        print(ConsoleLogger.error("Not a git repository."))
        sys.exit(1)

    base_branch = get_base_branch(root, branch)
    fork_point = run_git(["merge-base", "HEAD", base_branch], root) if base_branch else ""
    commits = get_commits(f"{fork_point}..HEAD", root) if fork_point else get_commits("HEAD", root, limit=15)

    if not commits:
        print(ConsoleLogger.info(f"No commits found on branch '{branch}' to analyze."))
        return

    print(f"\n{ConsoleLogger.BOLD}Deriving version bumps from branch: {ConsoleLogger.CYAN}{branch}{ConsoleLogger.RESET}")

    bumps = collect_bumps(root, commits)
    if not bumps:
        print(ConsoleLogger.info("No feat/fix/refactor/perf commits with component scopes found. Nothing to bump."))
        return

    rows = []
    new_versions: dict[str, str] = {}
    for comp_path, bump in sorted(bumps.items()):
        current = VERSIONS.get(comp_path, "")
        if current.endswith(".dev"):
            rows.append([comp_path, current, ConsoleLogger.info("SKIPPED (DEV)"), bump])
            continue
        if not has_unreleased_section(root, comp_path):
            rows.append([comp_path, current, ConsoleLogger.info("SKIPPED (no unreleased)"), bump])
            continue
        target = next_version(current, bump)
        if not target:
            rows.append([comp_path, current, ConsoleLogger.warning("SKIPPED (unparsable)"), bump])
            continue
        new_versions[comp_path] = target
        rows.append([comp_path, current, ConsoleLogger.success(target), bump])

    ConsoleLogger.print_table("Version Bump Plan", ["Component", "Current", "Target", "Bump"], rows)

    if not new_versions:
        print(ConsoleLogger.info("Nothing to apply."))
        return

    if args.dry_run:
        print(ConsoleLogger.info("Dry run: registry.py not modified."))
        return

    if not args.yes:
        choice = input(
            f"\n{ConsoleLogger.BOLD}{ConsoleLogger.YELLOW}Apply these bumps to .dev/registry.py? [y/N]: {ConsoleLogger.RESET}"
        ).strip().lower()
        if choice not in ("y", "yes"):
            print(ConsoleLogger.info("Operation aborted."))
            return

    apply_to_registry(new_versions)
    print(ConsoleLogger.success(f"\n[OK] registry.py updated for {len(new_versions)} component(s)."))
    print(ConsoleLogger.info("Next: run apply_versions.py to propagate to manifests and changelogs."))


if __name__ == "__main__":
    main()
