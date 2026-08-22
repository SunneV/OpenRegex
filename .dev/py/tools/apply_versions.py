import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent.parent
PY_DIR = SCRIPT_DIR.parent
UTILS_DIR = PY_DIR / "utils"

sys.path.insert(0, str(DEV_DIR))
sys.path.insert(0, str(UTILS_DIR))

from registry import VERSIONS
from logger import ConsoleLogger


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def check_changelog(root: Path, project: str, target_version: str) -> tuple[bool, str, bool]:
    if target_version.endswith(".dev"):
        return True, "", False

    changelog_path = root / project / "CHANGELOG.md"

    if not changelog_path.exists():
        return False, "Missing CHANGELOG.md", False

    content = changelog_path.read_text(encoding="utf-8")

    releases = re.findall(r"^## \[([^\]]+)\]", content, re.MULTILINE)
    released_versions = [r for r in releases if r.lower() != "unreleased"]
    latest_version = released_versions[0] if released_versions else None

    if target_version == latest_version:
        return True, "", False

    if not re.search(r"^## \[Unreleased\]", content, re.MULTILINE | re.IGNORECASE):
        return False, "No '## [Unreleased]'", False

    if re.search(rf"^## \[{re.escape(target_version)}\]", content, re.MULTILINE):
        return False, "Version already exists", False

    return True, "", True


def update_file(file_path: Path, pattern: str, replacement: str) -> tuple[str, str]:
    if not file_path.exists():
        return "SKIP", "File not found"

    content = file_path.read_text(encoding="utf-8")
    new_content, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)

    if count > 0:
        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return "OK", "Updated"
        else:
            return "OK", "No change"
    else:
        return "WARN", "Pattern not found"


def main():
    root = get_root_dir()
    results = []

    update_targets = {
        "apps/openregex-backend": [
            ("apps/openregex-backend/pyproject.toml", r'^version\s*=\s*"[^"]+"', 'version = "{}"'),
            ("deploy/dockerfiles/openregex-backend.dockerfile", r'^ENV APP_VERSION="[^"]+"', 'ENV APP_VERSION="{}"')
        ],
        "apps/openregex-frontend": [
            ("apps/openregex-frontend/package.json", r'"version"\s*:\s*"[^"]+"', '"version": "{}"'),
            ("deploy/dockerfiles/openregex-frontend.dockerfile", r'^ENV VITE_APP_VERSION="[^"]+"',
             'ENV VITE_APP_VERSION="{}"')
        ],
        "libs/python-shared": [
            ("libs/python-shared/pyproject.toml", r'^version\s*=\s*"[^"]+"', 'version = "{}"')
        ],
        "workers/worker-python": [
            ("workers/worker-python/pyproject.toml", r'^version\s*=\s*"[^"]+"', 'version = "{}"'),
            ("deploy/dockerfiles/worker-python.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-c-cpp": [
            ("workers/worker-c-cpp/pyproject.toml", r'^version\s*=\s*"[^"]+"', 'version = "{}"'),
            ("deploy/dockerfiles/worker-c-cpp.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-v8": [
            ("deploy/dockerfiles/worker-v8.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-rust": [
            ("deploy/dockerfiles/worker-rust.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-dotnet": [
            ("deploy/dockerfiles/worker-dotnet.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-jvm": [
            ("deploy/dockerfiles/worker-jvm.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-go": [
            ("deploy/dockerfiles/worker-go.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-php": [
            ("deploy/dockerfiles/worker-php.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ],
        "workers/worker-ai": [
            ("workers/worker-ai/pyproject.toml", r'^version\s*=\s*"[^"]+"', 'version = "{}"'),
            ("deploy/dockerfiles/worker-ai.dockerfile", r'^ENV WORKER_VERSION="[^"]+"', 'ENV WORKER_VERSION="{}"')
        ]
    }

    for project, target_version in VERSIONS.items():
        is_valid, error_msg, needs_changelog_update = check_changelog(root, project, target_version)

        if not is_valid:
            results.append([project, "CHANGELOG.md", ConsoleLogger.error(f"Aborted ({error_msg})"), target_version])
            continue

        targets = list(update_targets.get(project, []))

        if needs_changelog_update:
            targets.append(
                (f"{project}/CHANGELOG.md", r"^## \[Unreleased\].*", '## [{}] - YYYY-MM-DD')
            )

        if targets:
            for filepath, pattern, replacement_template in targets:
                file_path = root / filepath
                write_version = target_version

                if file_path.name == "pyproject.toml" and "-" in write_version:
                    write_version = write_version.replace("-", "+", 1)

                replacement = replacement_template.format(write_version)
                status, msg = update_file(file_path, pattern, replacement)

                color_msg = msg
                if status == "OK":
                    color_msg = ConsoleLogger.success(msg) if msg == "Updated" else ConsoleLogger.info(msg)
                elif status == "WARN":
                    color_msg = ConsoleLogger.warning(msg)
                elif status == "SKIP":
                    color_msg = ConsoleLogger.error(msg)

                results.append([project, filepath, color_msg, write_version])
        else:
            results.append([project, "N/A", ConsoleLogger.warning("No config found"), "N/A"])

    ConsoleLogger.print_table("Version Application Summary", ["Project", "File", "Status", "Version"], results)


if __name__ == "__main__":
    main()