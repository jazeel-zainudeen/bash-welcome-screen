#!/usr/bin/env bash
#
# Terminal Welcome Dashboard - Installer
# Sets up 'welcome' in ~/.local/bin and optionally adds startup hook to shell rc.
#

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_SRC="$REPO_DIR/welcome"
TARGET_DIR="${HOME}/.local/bin"
TARGET_BIN="$TARGET_DIR/welcome"
CONFIG_DIR="${HOME}/.config/welcome"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
AMBER='\033[0;33m'
RESET='\033[0m'

echo -e "${CYAN}=== Installing Terminal Welcome Dashboard ===${RESET}"

# 1. Check Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${AMBER}Error: Python 3 is required but not found in PATH.${RESET}"
    exit 1
fi

# 2. Ensure target bin directory exists
mkdir -p "$TARGET_DIR"

# 3. Create symlink for welcome and aliases
echo -e "Installing binary symlinks in ${GREEN}$TARGET_DIR${RESET}..."
chmod +x "$BIN_SRC"
ln -sf "$BIN_SRC" "$TARGET_BIN"
ln -sf "$BIN_SRC" "$TARGET_DIR/motd"
ln -sf "$BIN_SRC" "$TARGET_DIR/sysinfo"
ln -sf "$BIN_SRC" "$TARGET_DIR/welcome-screen"

# 4. Initialize configuration if not present
if [ ! -f "$CONFIG_FILE" ]; then
    mkdir -p "$CONFIG_DIR"
    cp "$REPO_DIR/config.example.json" "$CONFIG_FILE"
    echo -e "Created default configuration at ${GREEN}$CONFIG_FILE${RESET}"
else
    echo -e "Existing configuration found at ${GREEN}$CONFIG_FILE${RESET} (kept untouched)"
fi

# 5. Check PATH
if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
    echo -e "${AMBER}Note: $TARGET_DIR is not currently in your PATH.${RESET}"
    echo -e "Add this to your ~/.bashrc or ~/.zshrc:"
    echo -e "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# 6. Offer shell startup hook
HOOK='if [[ $- == *i* ]] && [ -x "$HOME/.local/bin/welcome" ]; then "$HOME/.local/bin/welcome"; fi'

for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$RC" ]; then
        if ! grep -Fq "welcome" "$RC"; then
            echo ""
            read -p "Would you like to auto-run welcome on interactive terminal launch in $(basename $RC)? [y/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "\n# Terminal Welcome Dashboard\n$HOOK" >> "$RC"
                echo -e "${GREEN}✓ Added startup hook to $RC${RESET}"
            fi
        else
            echo -e "${GREEN}✓ Startup hook already present in $(basename $RC)${RESET}"
        fi
    fi
done

echo ""
echo -e "${GREEN}✓ Installation complete!${RESET}"
echo -e "Run ${CYAN}welcome${RESET} to test the dashboard, or ${CYAN}welcome --help${RESET} for available options."
