#!/usr/bin/env bash
#
# Terminal Welcome Dashboard & SSH Manager - Installer
# Modular installer for 'welcome' and 'sshm'.
#

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$REPO_DIR/bin"
CONFIG_DIR="$REPO_DIR/config"
TARGET_DIR="${HOME}/.local/bin"
USER_CONFIG_DIR="${HOME}/.config/welcome"
USER_CONFIG_FILE="$USER_CONFIG_DIR/config.json"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
AMBER='\033[0;33m'
BOLD='\033[1m'
RESET='\033[0m'

INSTALL_WELCOME=false
INSTALL_SSHM=false
FLAG_PASSED=false
USER_CUSTOM_NAME=""

print_usage() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all            Install both welcome dashboard and sshm (default)"
    echo "  --welcome        Install only the welcome dashboard"
    echo "  --sshm           Install only the interactive SSH manager (sshm)"
    echo "  --name <name>    Set custom display name for greeting"
    echo "  --help, -h       Show this help message"
    echo ""
}

# Parse command line flags
while [ $# -gt 0 ]; do
    case "$1" in
        --all)
            INSTALL_WELCOME=true
            INSTALL_SSHM=true
            FLAG_PASSED=true
            shift
            ;;
        --welcome)
            INSTALL_WELCOME=true
            FLAG_PASSED=true
            shift
            ;;
        --sshm)
            INSTALL_SSHM=true
            FLAG_PASSED=true
            shift
            ;;
        --name)
            if [ -n "$2" ] && [[ "$2" != --* ]]; then
                USER_CUSTOM_NAME="$2"
                shift 2
            else
                echo -e "${AMBER}Error: --name requires a value.${RESET}"
                exit 1
            fi
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
done

# If no component flags passed, prompt or default to all
if [ "$FLAG_PASSED" = false ]; then
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
    chmod +x "$BIN_DIR/welcome"
    ln -sf "$BIN_DIR/welcome" "$TARGET_DIR/welcome"
    ln -sf "$BIN_DIR/welcome" "$TARGET_DIR/motd"
    ln -sf "$BIN_DIR/welcome" "$TARGET_DIR/sysinfo"
    ln -sf "$BIN_DIR/welcome" "$TARGET_DIR/welcome-screen"

    # Initialize configuration
    mkdir -p "$USER_CONFIG_DIR"
    if [ ! -f "$USER_CONFIG_FILE" ]; then
        cp "$CONFIG_DIR/config.example.json" "$USER_CONFIG_FILE"
        echo -e "Created configuration at ${GREEN}$USER_CONFIG_FILE${RESET}"
    else
        echo -e "Existing configuration found at ${GREEN}$USER_CONFIG_FILE${RESET}"
    fi

    # Display name customization
    DEFAULT_NAME="$(python3 -c "import os, pwd; u=os.getenv('USER') or os.getenv('LOGNAME') or 'User'; print(pwd.getpwuid(os.getuid()).pw_gecos.split(',')[0].strip() or u.capitalize())" 2>/dev/null || echo "User")"
    
    if [ -z "$USER_CUSTOM_NAME" ] && [ -t 0 ]; then
        echo ""
        read -p "Preferred display name for greeting [Default: $DEFAULT_NAME]: " INPUT_NAME
        USER_CUSTOM_NAME="${INPUT_NAME:-$DEFAULT_NAME}"
    fi

    if [ -n "$USER_CUSTOM_NAME" ] && [ -f "$USER_CONFIG_FILE" ]; then
        python3 -c "
import json
try:
    with open('$USER_CONFIG_FILE', 'r') as f:
        data = json.load(f)
    data['user_name'] = '''$USER_CUSTOM_NAME'''
    with open('$USER_CONFIG_FILE', 'w') as f:
        json.dump(data, f, indent=2)
except Exception:
    pass
"
        echo -e "Display name configured as: ${GREEN}$USER_CUSTOM_NAME${RESET}"
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
    chmod +x "$BIN_DIR/sshm"
    ln -sf "$BIN_DIR/sshm" "$TARGET_DIR/sshm"
    ln -sf "$BIN_DIR/sshm" "$TARGET_DIR/sshc"
    ln -sf "$BIN_DIR/sshm" "$TARGET_DIR/ssh-menu"
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
