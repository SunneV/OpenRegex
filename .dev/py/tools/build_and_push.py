#!/usr/bin/env python3
import os
import re
import subprocess
import sys
import datetime
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent.parent
PY_DIR = SCRIPT_DIR.parent
UTILS_DIR = PY_DIR / "utils"

sys.path.insert(0, str(DEV_DIR))
sys.path.insert(0, str(UTILS_DIR))

from registry import VERSIONS
from logger import ConsoleLogger

DOCKER_USERNAME = os.environ.get("DOCKER_USERNAME", "sunnev")

COMPONENT_NAMES = {
    "apps/openregex-frontend": "**OpenRegex Frontend**",
    "apps/openregex-backend": "**OpenRegex Backend**",
    "libs/python-shared": "**Python Shared Library**",
    "workers/worker-ai": "**Worker AI**",
    "workers/worker-python": "**Worker Python**",
    "workers/worker-c-cpp": "**Worker C/C++**",
    "workers/worker-dotnet": "**Worker .NET**",
    "workers/worker-go": "**Worker Go**",
    "workers/worker-jvm": "**Worker JVM**",
    "workers/worker-rust": "**Worker Rust**",
    "workers/worker-v8": "**Worker V8**",
    "workers/worker-php": "**Worker PHP**",
    "workers/worker-perl": "**Worker Perl**",
    "workers/worker-ruby": "**Worker Ruby**",
    "workers/worker-jvm8": "**Worker Java 8**",
    "workers/worker-postgres": "**Worker PostgreSQL**",
    "workers/worker-mysql": "**Worker MySQL**",
    "workers/worker-posix": "**Worker POSIX Tools**",
    "workers/worker-vim": "**Worker Vim**",
}


def tag_exists_on_remote(image_name, tag):
    full_image = f"{image_name}:{tag}"
    cmd = ["docker", "manifest", "inspect", full_image]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def run_command(cmd, cwd, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        print(f"{ConsoleLogger.RED}[ERROR] Command failed with exit code {result.returncode}{ConsoleLogger.RESET}")
        return False
    return True


def verify_component_changelog(changelog_path, version):
    if not os.path.exists(changelog_path):
        return False
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = rf"^##\s+\[{re.escape(version)}\](?:\s+-\s+.*)?$"
    return bool(re.search(pattern, content, re.MULTILINE))


def update_component_changelog_date(changelog_path, version, current_utc_date):
    if not os.path.exists(changelog_path):
        return False
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern_with_date = rf"^(##\s+\[{re.escape(version)}\]\s+-\s+)YYYY-MM-DD\s*$"
    pattern_without_date = rf"^(##\s+\[{re.escape(version)}\])\s*$"

    new_content = content
    if re.search(pattern_with_date, content, re.MULTILINE):
        new_content = re.sub(pattern_with_date, rf"\g<1>{current_utc_date}", content, flags=re.MULTILINE)
    elif re.search(pattern_without_date, content, re.MULTILINE):
        new_content = re.sub(pattern_without_date, rf"\g<1> - {current_utc_date}", content, flags=re.MULTILINE)
    else:
        return False

    if new_content != content:
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def parse_changelog(changelog_path):
    if not os.path.exists(changelog_path):
        return [], -1, -1, {}

    with open(changelog_path, 'r', encoding="utf-8") as f:
        lines = f.read().splitlines()

    table_start = -1
    table_end = -1
    in_table = False

    for i, line in enumerate(lines):
        if line.startswith("| Component"):
            in_table = True
            table_start = i
        if in_table:
            if not line.strip().startswith("|"):
                table_end = i
                break

    if in_table and table_end == -1:
        table_end = len(lines)

    state = {}
    if table_start != -1:
        headers = [h.strip() for h in lines[table_start].split("|")][1:-1]
        has_changelog = "Changelog" in headers

        o_idx = 2 if has_changelog else 1
        r_idx = 3 if has_changelog else 2
        d_idx = 4 if has_changelog else 3
        dr_idx = 5 if has_changelog else 4

        for line in lines[table_start:table_end]:
            if "---" in line or "Component" in line:
                continue
            parts = [p.strip() for p in line.split("|")][1:-1]
            if not parts:
                continue

            comp = parts[0]
            state[comp] = {
                "Official Version": parts[o_idx] if len(parts) > o_idx else "N/A",
                "release date": parts[r_idx] if len(parts) > r_idx else "N/A",
                "Develop Version": parts[d_idx] if len(parts) > d_idx else "N/A",
                "dev release date": parts[dr_idx] if len(parts) > dr_idx else "N/A"
            }

        family_key = "**Worker Family (All)**"
        if family_key in state:
            family_state = state.pop(family_key)
            for path in VERSIONS.keys():
                if path.startswith("workers/"):
                    c_name = COMPONENT_NAMES.get(path)
                    if c_name and c_name not in state:
                        state[c_name] = family_state.copy()

    return lines, table_start, table_end, state


def write_changelog(changelog_path, lines, table_start, table_end, state, update_date_dash):
    new_table = [
        "| Component | Changelog | Official Version | release date | Develop Version | dev release date |",
        "|:---|:---|:---|---|---|---|"
    ]

    for comp_path in COMPONENT_NAMES.keys():
        comp_name = COMPONENT_NAMES[comp_path]
        if comp_name in state:
            s = state[comp_name]
            changelog_link = f"[View](./{comp_path}/CHANGELOG.md)"
            new_table.append(
                f"| {comp_name} | {changelog_link} | {s['Official Version']} | {s['release date']} | {s['Develop Version']} | {s['dev release date']} |"
            )

    if table_start != -1:
        lines[table_start:table_end] = new_table
    else:
        lines.extend(new_table)

    for i, line in enumerate(lines):
        if line.startswith("**Last Update:"):
            lines[i] = f"**Last Update: {update_date_dash}**"
            break

    with open(changelog_path, 'w', encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def update_state_for_component(state, comp_name, registry_version, is_dev, date_dot, force_update=False):
    if comp_name not in state:
        state[comp_name] = {
            "Official Version": "N/A",
            "release date": "N/A",
            "Develop Version": "N/A",
            "dev release date": "N/A"
        }

    formatted_ver = f"`{registry_version}`"
    updated = False

    if is_dev:
        if state[comp_name]["Develop Version"] != formatted_ver or force_update:
            state[comp_name]["Develop Version"] = formatted_ver
            state[comp_name]["dev release date"] = date_dot
            updated = True
    else:
        if state[comp_name]["Official Version"] != formatted_ver or force_update:
            state[comp_name]["Official Version"] = formatted_ver
            state[comp_name]["release date"] = date_dot
            updated = True

    return updated


def main():
    parser = argparse.ArgumentParser(description="Build and push Docker images for OpenRegex.")
    parser.add_argument("--fake-push", action="store_true", help="Skip the actual docker push.")
    args = parser.parse_args()

    fake_push_mode = args.fake_push

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    changelog_path = os.path.join(project_root, "CHANGELOG.md")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    current_utc_date = now_utc.strftime("%Y-%m-%d")
    current_utc_dot = now_utc.strftime("%Y.%m.%d")

    lines, table_start, table_end, state = parse_changelog(changelog_path)

    pre_exec_table = []
    execution_tasks = []

    print(f"\n{ConsoleLogger.BOLD}Gathering data and checking remote registries...{ConsoleLogger.RESET}")
    total_versions = len(VERSIONS)

    for idx, (component_path, registry_version) in enumerate(VERSIONS.items(), start=1):
        component_name = os.path.basename(component_path)
        pretty_name = COMPONENT_NAMES.get(component_path, component_name)

        ConsoleLogger.progress_bar(idx, total_versions, prefix="Scanning", suffix=f"Checking {component_name}...")

        is_lib = component_path.startswith("libs/")
        is_dev = registry_version.endswith(".dev")

        comp_changelog_path = os.path.join(project_root, component_path, "CHANGELOG.md")

        if is_dev:
            cl_exists = True
            cl_status = "IGNORED (DEV)"
        else:
            cl_exists = verify_component_changelog(comp_changelog_path, registry_version)
            cl_status = "FOUND" if cl_exists else "MISSING"

        image_repo_name = component_name if component_name.startswith("openregex-") else f"openregex-{component_name}"
        image_name = f"{DOCKER_USERNAME}/{image_repo_name}"
        docker_tag = f"{image_name}:{registry_version}"

        remote_status_text = "NOT_CHECKED"
        action = ""

        dockerfile_path = os.path.join("deploy", "dockerfiles", f"{component_name}.dockerfile")
        full_dockerfile_path = os.path.join(project_root, dockerfile_path)

        if is_lib:
            action = "SKIP_LIBRARY"
        elif not os.path.exists(full_dockerfile_path):
            action = "SKIP_MISSING_DOCKERFILE"
        else:
            if cl_exists:
                if tag_exists_on_remote(image_name, registry_version):
                    remote_status_text = "EXISTS"
                    action = "SKIP_ALREADY_PUBLISHED"
                else:
                    remote_status_text = "NOT_EXISTS"
                    action = "BUILD_AND_PUSH"
            else:
                action = "SKIP_CHANGELOG_VERSION_MISSING"

        if cl_status == "FOUND":
            c_cl_status = ConsoleLogger.success(cl_status)
        elif cl_status == "IGNORED (DEV)":
            c_cl_status = ConsoleLogger.info(cl_status)
        else:
            c_cl_status = ConsoleLogger.error(cl_status)

        c_rem_status = remote_status_text
        if remote_status_text == "EXISTS":
            c_rem_status = ConsoleLogger.warning(remote_status_text)
        elif remote_status_text == "NOT_EXISTS":
            c_rem_status = ConsoleLogger.success(remote_status_text)
        elif remote_status_text == "NOT_CHECKED":
            c_rem_status = ConsoleLogger.info(remote_status_text)

        c_action = action
        if action == "BUILD_AND_PUSH":
            c_action = ConsoleLogger.success(action)
        elif action.startswith("SKIP"):
            c_action = ConsoleLogger.warning(action)

        pre_exec_table.append([pretty_name, registry_version, c_cl_status, c_rem_status, c_action])

        if "frontend" in component_name:
            date_arg_name = "VITE_APP_RELEASE_DATE"
        elif "backend" in component_name:
            date_arg_name = "APP_RELEASE_DATE"
        else:
            date_arg_name = "WORKER_RELEASE_DATE"

        execution_tasks.append({
            "pretty": pretty_name,
            "version": registry_version,
            "action": action,
            "docker_tag": docker_tag,
            "image_repo_name": image_repo_name,
            "dockerfile_path": dockerfile_path,
            "date_arg_name": date_arg_name,
            "comp_changelog_path": comp_changelog_path,
            "latest_tag": f"{image_name}:latest",
            "is_dev": is_dev
        })

    ConsoleLogger.print_table("Pre-Execution Overview",
                              ["Component", "Target Version", "Changelog Status", "Remote Status", "Action"],
                              pre_exec_table)

    if not execution_tasks:
        print(ConsoleLogger.info("\nNo execution tasks required. Everything is up to date."))
        return

    needs_build = any(t['action'] == "BUILD_AND_PUSH" for t in execution_tasks)

    if needs_build:
        try:
            prompt = f"\n{ConsoleLogger.BOLD}{ConsoleLogger.YELLOW}Do you want to proceed with execution based on the plan above? [y/N]: {ConsoleLogger.RESET}"
            choice = input(prompt).strip().lower()
            if choice not in ['y', 'yes']:
                print(ConsoleLogger.info("Operation aborted by user."))
                return
        except KeyboardInterrupt:
            print(ConsoleLogger.info("\nOperation aborted by user."))
            return
        print(ConsoleLogger.info("\nStarting execution...\n"))
    else:
        print(ConsoleLogger.info("\nNo build and push tasks required. Proceeding to finalize summary...\n"))

    post_exec_table = []
    root_summary_updated = False

    for task in execution_tasks:
        pretty = task['pretty']
        version = task['version']
        action = task['action']
        docker_tag = task['docker_tag']
        is_dev = task['is_dev']

        if action == "SKIP_LIBRARY":
            # Libraries ship inside other images, but their changelog release
            # date must still be stamped when the version goes official.
            cl_updated = False
            if not is_dev:
                cl_updated = update_component_changelog_date(task['comp_changelog_path'], version, current_utc_date)
            state_updated = update_state_for_component(state, pretty, version, is_dev, current_utc_dot)
            if state_updated: root_summary_updated = True
            post_exec_table.append(
                [pretty, version, action, ConsoleLogger.info("SKIPPED"), "YES" if cl_updated else "NO",
                 "YES" if state_updated else "NO"])
            continue

        if action in ("SKIP_MISSING_DOCKERFILE", "SKIP_CHANGELOG_VERSION_MISSING", "SKIP_ALREADY_PUBLISHED"):
            post_exec_table.append([pretty, version, action, ConsoleLogger.info("SKIPPED"), "NO", "NO"])
            continue

        if action == "BUILD_AND_PUSH":
            print(f"\n{ConsoleLogger.CYAN}[BUILD]{ConsoleLogger.RESET} {task['image_repo_name']} ({version})")
            build_cmd = ["docker", "build", "-f", task["dockerfile_path"], "-t", docker_tag,
                         "--build-arg", f"{task['date_arg_name']}={current_utc_date}", "."]
            if not is_dev:
                build_cmd.extend(["-t", task["latest_tag"]])

            build_success = run_command(build_cmd, cwd=project_root)

            push_success = False
            if build_success:
                if not fake_push_mode:
                    print(f"{ConsoleLogger.CYAN}[PUSH]{ConsoleLogger.RESET} {task['image_repo_name']}...")
                    push_success = run_command(["docker", "push", docker_tag], cwd=project_root)
                    if push_success and not is_dev:
                        run_command(["docker", "push", task["latest_tag"]], cwd=project_root)
                else:
                    print(f"{ConsoleLogger.YELLOW}[FAKE PUSH]{ConsoleLogger.RESET} Skipped docker push.")
                    push_success = True

            if build_success and push_success:
                cl_updated = False
                if not is_dev:
                    cl_updated = update_component_changelog_date(task['comp_changelog_path'], version, current_utc_date)

                state_updated = update_state_for_component(state, pretty, version, is_dev, current_utc_dot,
                                                           force_update=True)
                if state_updated: root_summary_updated = True

                post_exec_table.append(
                    [pretty, version, action, ConsoleLogger.success("SUCCESS"), "YES" if cl_updated else "NO",
                     "YES" if state_updated else "NO"])
            else:
                post_exec_table.append([pretty, version, action, ConsoleLogger.error("FAILED"), "NO", "NO"])

    ConsoleLogger.print_table("Post-Execution Summary",
                              ["Component", "Target Version", "Action", "Result", "Changelog Updated",
                               "Root Summary Updated"],
                              post_exec_table)

    if root_summary_updated and table_start != -1:
        write_changelog(changelog_path, lines, table_start, table_end, state, current_utc_date)
        print(ConsoleLogger.success("\n[OK] Root CHANGELOG.md summary updated successfully."))
    else:
        print(ConsoleLogger.success("\n[OK] Execution complete. No changes required in Root CHANGELOG.md summary."))


if __name__ == "__main__":
    main()