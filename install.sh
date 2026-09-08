#!/usr/bin/env bash
#
# Terminal Welcome Dashboard & SSH Manager - Installer
# Modular installer for 'welcome' and 'sshm'.
#

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/welcome"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
AMBER='\033[0;33m'
BOLD='\033[1m'
RESET='\033[0m'

INSTALL_WELCOME=false
INSTALL_SSHM=false

print_usage() {
    echo "Usage: ./install.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --all        Install both welcome dashboard and sshm (default)"
    echo "  --welcome    Install only the welcome dashboard"
    echo "  --sshm       Install only the interactive SSH manager (sshm)"
    echo "  --help, -h   Show this help message"
    echo ""
}

# Parse command line flags
if [ $# -gt 0 ]; then
    case "$1" in
        --all)
            INSTALL_WELCOME=true
            INSTALL_SSHM=true
            ;;
        --welcome)
            INSTALL_WELCOME=true
            ;;
        --sshm)
            INSTALL_SSHM=true
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${AMBER}Unknown option: $1${RESET}"
            print_usage
            exit 1
            ;;
    esac
else
    # Interactive selection if running in a terminal
    if [ -t 0 ]; then
        echo -e "${CYAN}${BOLD}=== Terminal Welcome & SSH Tools Setup ===${RESET}"
        echo "Choose components to install:"
        echo -e "  ${BOLD}1)${RESET} All (Welcome Dashboard + Interactive SSH Manager sshm) ${GREEN}[Default]${RESET}"
        echo -e "  ${BOLD}2)${RESET} Welcome Dashboard only (welcome)"
        echo -e "  ${BOLD}3)${RESET} Interactive SSH Manager only (sshm)"
        echo ""
        read -p "Select option [1-3, default 1]: " choice
        case "$choice" in
            2)
                INSTALL_WELCOME=true
                ;;
            3)
                INSTALL_SSHM=true
                ;;
            *)
                INSTALL_WELCOME=true
                INSTALL_SSHM=true
                ;;
        esac
    else
        INSTALL_WELCOME=true
        INSTALL_SSHM=true
    fi
fi

# 1. Check Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${AMBER}Error: Python 3 is required but not found in PATH.${RESET}"
    exit 1
fi

mkdir -p "$TARGET_DIR"

# 2. Install Welcome Dashboard
if [ "$INSTALL_WELCOME" = true ]; then
    echo -e "\n${CYAN}--> Installing Welcome Dashboard...${RESET}"
    chmod +x "$REPO_DIR/welcome"
    ln -sf "$REPO_DIR/welcome" "$TARGET_DIR/welcome"
    ln -sf "$REPO_DIR/welcome" "$TARGET_DIR/motd"
    ln -sf "$REPO_DIR/welcome" "$TARGET_DIR/sysinfo"
    ln -sf "$REPO_DIR/welcome" "$TARGET_DIR/welcome-screen"

    # Initialize configuration if not present
    if [ ! -f "$CONFIG_FILE" ]; then
        mkdir -p "$CONFIG_DIR"
        cp "$REPO_DIR/config.example.json" "$CONFIG_FILE"
        echo -e "Created default configuration at ${GREEN}$CONFIG_FILE${RESET}"
    else
        echo -e "Existing configuration found at ${GREEN}$CONFIG_FILE${RESET} (kept untouched)"
    fi

    # Shell startup hook
    HOOK='if [[ $- == *i* ]] && [ -x "$HOME/.local/bin/welcome" ]; then "$HOME/.local/bin/welcome"; fi'
    for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
        if [ -f "$RC" ]; then
            if ! grep -Fq "welcome" "$RC"; then
                if [ -t 0 ]; then
                    read -p "Auto-run welcome on interactive terminal launch in $(basename $RC)? [y/N] " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        echo -e "\n# Terminal Welcome Dashboard\n$HOOK" >> "$RC"
                        echo -e "${GREEN}✓ Added startup hook to $RC${RESET}"
                    fi
                fi
            else
                echo -e "${GREEN}✓ Startup hook already present in $(basename $RC)${RESET}"
            fi
        fi
    done
fi

# 3. Install SSH Manager (sshm)
if [ "$INSTALL_SSHM" = true ]; then
    echo -e "\n${CYAN}--> Installing Interactive SSH Manager (sshm)...${RESET}"
    chmod +x "$REPO_DIR/sshm"
    ln -sf "$REPO_DIR/sshm" "$TARGET_DIR/sshm"
    ln -sf "$REPO_DIR/sshm" "$TARGET_DIR/sshc"
    ln -sf "$REPO_DIR/sshm" "$TARGET_DIR/ssh-menu"
    echo -e "${GREEN}✓ Installed sshm, sshc, and ssh-menu symlinks in $TARGET_DIR${RESET}"
fi

# 4. PATH check
if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
    echo -e "\n${AMBER}Note: $TARGET_DIR is not currently in your PATH.${RESET}"
    echo -e "Add this to your ~/.bashrc or ~/.zshrc:"
    echo -e "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo -e "\n${GREEN}${BOLD}✓ Installation complete!${RESET}"
if [ "$INSTALL_WELCOME" = true ]; then
    echo -e "  • Dashboard   : run ${CYAN}welcome${RESET} or ${CYAN}welcome --help${RESET}"
fi
if [ "$INSTALL_SSHM" = true ]; then
    echo -e "  • SSH Manager : run ${CYAN}sshm${RESET} or ${CYAN}sshm --help${RESET}"
fi
echo ""
