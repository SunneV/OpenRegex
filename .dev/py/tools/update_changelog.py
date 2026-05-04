import sys
import argparse
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent.parent
PY_DIR = SCRIPT_DIR.parent
UTILS_DIR = PY_DIR / "utils"

sys.path.insert(0, str(DEV_DIR))
sys.path.insert(0, str(UTILS_DIR))

from registry import VERSIONS
from logger import ConsoleLogger
from git import run_git, run_git_lines


def get_root_dir() -> Path:
    return SCRIPT_DIR.parent.parent.parent


def get_base_branch(root: Path, current_branch: str) -> str:
    candidates = ["develop", "main", "master", "origin/develop", "origin/main", "origin/master"]
    for cand in candidates:
        if current_branch == cand or f"origin/{current_branch}" == cand:
            continue
        if run_git(["rev-parse", "--verify", "--quiet", cand], root):
            return cand
    return ""


def get_commits(rev_range: str, cwd: Path, limit: int = 0) -> list[list[str]]:
    args = ["log", "--format=%h|%s"]
    if limit > 0:
        args.extend(["-n", str(limit)])
    args.append(rev_range)

    output = run_git(args, cwd)
    if not output:
        return []

    rows = []
    for line in output.splitlines():
        parts = line.split("|", 1)
        if len(parts) == 2:
            rows.append([parts[0], parts[1]])
    return rows


def get_component_path_by_scope(scope: str) -> str:
    scope_map = {
        "backend": "apps/openregex-backend",
        "frontend": "apps/openregex-frontend",
        "shared-lib": "libs/python-shared"
    }

    if scope in scope_map:
        return scope_map[scope]

    for path in VERSIONS.keys():
        if scope in path:
            return path
    return ""


def process_changelog_entries(root: Path, entries: list[dict]) -> list[str]:
    comp_entries = {}
    for entry in entries:
        scope = entry.get("scope")
        if not scope:
            continue
        comp_path = get_component_path_by_scope(scope)
        if not comp_path:
            continue
        if comp_path not in comp_entries:
            comp_entries[comp_path] = []
        comp_entries[comp_path].append(entry)

    modified_files = []
    for comp_path, centries in comp_entries.items():
        changelog_file = root / comp_path / "CHANGELOG.md"
        if _update_changelog_file(changelog_file, centries):
            modified_files.append(f"{comp_path}/CHANGELOG.md")
            print(ConsoleLogger.success(f"Updated {comp_path}/CHANGELOG.md"))

    return modified_files


def _update_changelog_file(file_path: Path, entries: list[dict]) -> bool:
    if not file_path.exists():
        print(ConsoleLogger.error(f"[ERROR] Changelog not found at {file_path}. Skipping."))
        return False

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    updates_by_type = {}
    for entry in entries:
        t = entry.get("type")
        msg = entry.get("message")
        if not t or not msg:
            continue
        if t not in updates_by_type:
            updates_by_type[t] = []
        updates_by_type[t].append(msg)

    if not updates_by_type:
        return False

    unreleased_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("## [Unreleased]"):
            unreleased_idx = i
            break

    if unreleased_idx == -1:
        insert_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                insert_idx = i
                break

        if insert_idx != -1:
            lines.insert(insert_idx, "## [Unreleased] - YYYY-MM-DD")
            unreleased_idx = insert_idx
        else:
            lines.append("## [Unreleased] - YYYY-MM-DD")
            unreleased_idx = len(lines) - 1

    next_release_idx = len(lines)
    for i in range(unreleased_idx + 1, len(lines)):
        if lines[i].startswith("## ["):
            next_release_idx = i
            break

    inserted_any = False
    for c_type, messages in updates_by_type.items():
        type_header = f"### {c_type}"
        type_idx = -1

        for i in range(unreleased_idx + 1, next_release_idx):
            if lines[i].startswith(type_header):
                type_idx = i
                break

        if type_idx == -1:
            insert_pos = next_release_idx
            lines.insert(insert_pos, type_header)
            for j, msg in enumerate(messages):
                lines.insert(insert_pos + 1 + j, f"- {msg}")
            next_release_idx += len(messages) + 1
            inserted_any = True
        else:
            insert_pos = type_idx + 1
            for msg in messages:
                exists = False
                for k in range(type_idx + 1, next_release_idx):
                    if lines[k].startswith("### "):
                        break
                    if msg in lines[k]:
                        exists = True
                        break
                if not exists:
                    lines.insert(insert_pos, f"- {msg}")
                    next_release_idx += 1
                    insert_pos += 1
                    inserted_any = True

    if inserted_any:
        raw_content = "\n".join(lines)

        # Standardize spacing: Collapse 3+ newlines into 2 (1 blank line)
        raw_content = re.sub(r'\n{3,}', '\n\n', raw_content)

        # Ensure exactly 1 blank line before any ## or ### (if preceded by text)
        raw_content = re.sub(r'([^\n])\n(#{2,3} )', r'\1\n\n\2', raw_content)

        file_path.write_text(raw_content.strip() + "\n", encoding="utf-8")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Update component changelogs based on commit messages.")
    parser.add_argument("--commits", type=str, nargs="+", help="Specific commit hashes to analyze")
    args = parser.parse_args()

    root = get_root_dir()
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)

    if not branch:
        print(ConsoleLogger.error("Not a git repository."))
        return

    branch_commits = []
    if args.commits:
        for c in args.commits:
            subject = run_git(["show", "-s", "--format=%s", c], root)
            branch_commits.append([c, subject])
    else:
        base_branch = get_base_branch(root, branch)
        fork_point = run_git(["merge-base", "HEAD", base_branch], root) if base_branch else ""

        if fork_point:
            branch_commits = get_commits(f"{fork_point}..HEAD", root)
        else:
            branch_commits = get_commits("HEAD", root, limit=15)

    if not branch_commits:
        print(ConsoleLogger.error(f"No commits found on branch '{branch}' to analyze."))
        return

    print(f"\n{ConsoleLogger.BOLD}Analyzing commits on branch: {ConsoleLogger.CYAN}{branch}{ConsoleLogger.RESET}")

    pattern = re.compile(r"^(feat|fix|refactor|perf)\(([^)]+)\)!?:\s*(.+)$", re.MULTILINE)
    type_map = {"feat": "Added", "fix": "Fixed", "refactor": "Changed", "perf": "Changed"}

    entries = []
    table_rows = []

    for commit_hash, subject in branch_commits:
        msg = run_git(["show", "-s", "--format=%B", commit_hash], root)
        display_subject = subject[:65] + "..." if len(subject) > 65 else subject

        matches = pattern.findall(msg)
        if matches:
            table_rows.append([commit_hash, ConsoleLogger.success("Valid"), display_subject])
            for c_type_raw, scope, msg_subject in matches:
                entries.append({
                    "scope": scope,
                    "type": type_map.get(c_type_raw),
                    "message": msg_subject
                })
        else:
            table_rows.append([commit_hash, ConsoleLogger.error("Invalid"), display_subject])

    ConsoleLogger.print_table("Commit Analysis Results", ["Hash", "Status", "Subject"], table_rows)

    if not entries:
        print(ConsoleLogger.warning("No valid conventional commit headers found (feat, fix, refactor, perf)."))
        return

    choice = input(
        f"\n{ConsoleLogger.BOLD}{ConsoleLogger.YELLOW}Proceed with updating changelogs based on valid commits? [y/N]: {ConsoleLogger.RESET}").strip().lower()

    if choice in ['y', 'yes']:
        modified = process_changelog_entries(root, entries)
        if not modified:
            print(ConsoleLogger.info("No changelogs were updated (files missing or entries already exist)."))
    else:
        print(ConsoleLogger.info("Operation aborted."))


if __name__ == "__main__":
    main()