# OpenRegex Monorepo: Release & Branching Guidelines

This document outlines the standard procedures for managing versions, releasing components, and handling git branches
within the OpenRegex monorepo.

---

## 1. Release Strategy: Independent Versioning

OpenRegex uses an **Independent Versioning** model. Each component (apps, workers, and libs) has its own version cycle
defined in the central registry.

### The Source of Truth: `registry.py`

All versions are managed in `.dev/registry.py`. This file acts as the single source of truth for the entire
ecosystem.

### Automated Changelog & Manifest Synchronization

All release tooling lives in `.dev/py/tools/` (menu runner: `.dev/scripts/run.bat`).
The full chain, in order:

1. **Changelog Routing (`update_changelog.py`):** Parses labeled branch commits
   (`feat|fix|refactor|perf(scope):`) and appends entries to each component's
   `CHANGELOG.md` under `[Unreleased]`. Component changelogs are updated ONLY
   through this script.
2. **Version Bumping (`bump_versions.py`):** Derives per-component bumps from the
   same commit labels (`!`/BREAKING -> major, `feat` -> minor, `fix`/`refactor`/
   `perf` -> patch) and updates `.dev/registry.py`. Components without an
   `[Unreleased]` section are never bumped twice.
3. **Version Propagation (`apply_versions.py`):** Updates `pyproject.toml`,
   `package.json`, and Dockerfiles based on the registry and promotes
   `[Unreleased]` to the target version header.
4. **Verification (`check_unreleased.py`):** Confirms no component still has
   unreleased entries.
5. **Changelog & Build (`build_and_push.py`):**
    * It parses the "Component Version Snapshot" table in the root `CHANGELOG.md`.
    * It updates the "Official Version" and "Release Date" columns automatically based on successful builds.
    * It updates the "Last Update" timestamp at the top of the platform log.

---

## 2. Automatic Commit System

To ensure that version bumps and changelog updates are never lost, the following automated commit flow should be used (
currently manual, moving to CI/CD):

### Local Automation Sequence

After committing labeled work on a branch, run this sequence (or use
`.dev/scripts/run.bat` option **[10] Full Release Sync**):

```bash
# 1. Route changelog entries from commit labels
python .dev/py/tools/update_changelog.py --yes

# 2. Bump versions in the registry from the same labels
python .dev/py/tools/bump_versions.py --yes

# 3. Sync all version manifests and promote changelogs
python .dev/py/tools/apply_versions.py

# 4. Verify nothing is left unreleased
python .dev/py/tools/check_unreleased.py

# 5. Build images and update the root CHANGELOG.md table
python .dev/py/tools/build_and_push.py
```

---

## 3. Branching Strategy

To maintain code quality and stability, we follow a feature-branch workflow.

### Branch Types

| Branch Prefix | Purpose                                            | Example                      |
|:--------------|:---------------------------------------------------|:-----------------------------|
| `main`        | Production-ready code. Only updated via releases.  | `main`                       |
| `develop`     | Integration branch for the next release.           | `develop`                    |
| `feature/`    | New functionality or engine support.               | `feature/worker-zig-support` |
| `fix/`        | Bug fixes and ReDoS security patches.              | `fix/v8-memory-leak`         |
| `chore/`      | Maintenance, dependency updates, or documentation. | `chore/update-readme`        |

---

## 4. Future Automation (CI/CD)

**Note:** The current manual execution of scripts is a transitional phase.

---

## 5. Tagging Convention

For monorepo clarity, use prefixed tags:
``
* Format: `<folder>/<component-name>@<version>`
* Example: `workers/worker-php@1.0.1`

