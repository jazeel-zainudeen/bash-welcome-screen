#!/usr/bin/env bash
#
# Terminal Welcome Dashboard - Uninstaller
#

set -e

TARGET_DIR="${HOME}/.local/bin"
RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

echo -e "${RED}=== Uninstalling Terminal Welcome Dashboard ===${RESET}"

# Remove binary symlinks
for bin in welcome motd sysinfo welcome-screen; do
    if [ -L "$TARGET_DIR/$bin" ] || [ -f "$TARGET_DIR/$bin" ]; then
        rm -f "$TARGET_DIR/$bin"
        echo -e "Removed ${TARGET_DIR}/$bin"
    fi
done

echo ""
read -p "Do you also want to remove your config (~/.config/welcome) and notes (~/.welcome_notes)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "${HOME}/.config/welcome"
    rm -f "${HOME}/.welcome_notes"
    echo -e "Removed configuration and notes."
fi

echo ""
echo -e "${GREEN}✓ Uninstallation complete.${RESET}"
echo -e "Note: If you enabled the startup hook in ~/.bashrc or ~/.zshrc, you may remove those lines manually."
