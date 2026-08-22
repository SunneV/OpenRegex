@echo off
setlocal enabledelayedexpansion

:: Set directories based on the script location
set SCRIPT_DIR=%~dp0
set PY_DIR=!SCRIPT_DIR!..\py

echo ====================================
echo OpenRegex Dev Tools Runner
echo ====================================
echo [1] Apply Versions
echo [2] Build and Push
echo [3] Branch Status
echo [4] Check Scopes
echo [5] AI Commit: Amend Latest
echo [6] AI Commit: Squash Commits
echo [7] Update Changelog (Current Branch)
echo [8] Check Unreleased Changelogs
echo [9] Bump Versions (from commit labels)
echo [10] Full Release Sync (changelogs ^> bumps ^> manifests ^> check)
echo ====================================
set /p choice="Select task to run: "

if "!choice!"=="1" (
    echo Running apply_versions.py...
    python "!PY_DIR!\tools\apply_versions.py"
) else if "!choice!"=="2" (
    echo Running build_and_push.py...
    python "!PY_DIR!\tools\build_and_push.py"
) else if "!choice!"=="3" (
    echo Running branch_status.py...
    python "!PY_DIR!\tools\branch_status.py"
) else if "!choice!"=="4" (
    echo Running check_scopes.py...
    python "!PY_DIR!\tools\check_scopes.py"
) else if "!choice!"=="5" (
    echo Running ai_commit.py - Amend...
    python "!PY_DIR!\tools\ai_commit.py" --amend
) else if "!choice!"=="6" (
    echo Running ai_commit.py - Interactive Squash...
    python "!PY_DIR!\tools\ai_commit.py" --squash-interactive
) else if "!choice!"=="7" (
    echo Running update_changelog.py...
    python "!PY_DIR!\tools\update_changelog.py"
) else if "!choice!"=="8" (
    echo Running check_unreleased.py...
    python "!PY_DIR!\tools\check_unreleased.py"
) else if "!choice!"=="9" (
    echo Running bump_versions.py...
    python "!PY_DIR!\tools\bump_versions.py"
) else if "!choice!"=="10" (
    echo [1/4] Updating changelogs from commit labels...
    python "!PY_DIR!\tools\update_changelog.py" --yes
    if errorlevel 1 goto :sync_failed
    echo [2/4] Bumping versions in registry.py...
    python "!PY_DIR!\tools\bump_versions.py" --yes
    if errorlevel 1 goto :sync_failed
    echo [3/4] Propagating versions to manifests and changelogs...
    python "!PY_DIR!\tools\apply_versions.py"
    if errorlevel 1 goto :sync_failed
    echo [4/4] Verifying unreleased changelogs...
    python "!PY_DIR!\tools\check_unreleased.py"
    if errorlevel 1 goto :sync_failed
    echo Full release sync finished.
) else (
    echo Invalid choice.
)

goto :end

:sync_failed
echo Full release sync FAILED - fix the reported step before continuing.

:end
pause
