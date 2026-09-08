#!/usr/bin/env bash
#
# Terminal Welcome Dashboard & SSH Manager - Installer
# Interactive TUI and modular CLI installer for 'welcome' and 'sshm'.
#

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_SCRIPT="$REPO_DIR/scripts/installer.py"

# Verify Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "\033[0;31mError: Python 3 is required but not found in PATH.\033[0m"
    echo "Please install Python 3 (e.g. 'sudo apt install python3') and re-run this script."
    exit 1
fi

if [ -f "$INSTALLER_SCRIPT" ]; then
    exec python3 "$INSTALLER_SCRIPT" "$@"
else
    echo -e "\033[0;31mError: Installer engine not found at $INSTALLER_SCRIPT\033[0m"
    exit 1
fi
