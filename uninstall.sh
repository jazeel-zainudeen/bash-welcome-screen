#!/usr/bin/env bash
#
# Terminal Welcome Dashboard & SSH Manager - Uninstaller
#

set -e

TARGET_DIR="${HOME}/.local/bin"
RED='\033[0;31m'
GREEN='\033[0;32m'
AMBER='\033[0;33m'
BOLD='\033[1m'
RESET='\033[0m'

REMOVE_WELCOME=false
REMOVE_SSHM=false

print_usage() {
    echo "Usage: ./uninstall.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  --all        Remove both welcome dashboard and sshm"
    echo "  --welcome    Remove only the welcome dashboard"
    echo "  --sshm       Remove only the interactive SSH manager (sshm)"
    echo "  --help, -h   Show this help message"
    echo ""
}

if [ $# -gt 0 ]; then
    case "$1" in
        --all)
            REMOVE_WELCOME=true
            REMOVE_SSHM=true
            ;;
        --welcome)
            REMOVE_WELCOME=true
            ;;
        --sshm)
            REMOVE_SSHM=true
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
    if [ -t 0 ]; then
        echo -e "${RED}${BOLD}=== Uninstall Terminal Welcome & SSH Tools ===${RESET}"
        echo "Choose components to remove:"
        echo -e "  ${BOLD}1)${RESET} Remove All (welcome + sshm)"
        echo -e "  ${BOLD}2)${RESET} Remove Welcome Dashboard only"
        echo -e "  ${BOLD}3)${RESET} Remove SSH Manager (sshm) only"
        echo ""
        read -p "Select option [1-3, default 1]: " choice
        case "$choice" in
            2)
                REMOVE_WELCOME=true
                ;;
            3)
                REMOVE_SSHM=true
                ;;
            *)
                REMOVE_WELCOME=true
                REMOVE_SSHM=true
                ;;
        esac
    else
        REMOVE_WELCOME=true
        REMOVE_SSHM=true
    fi
fi

# Remove Welcome binaries
if [ "$REMOVE_WELCOME" = true ]; then
    echo -e "\nRemoving Welcome Dashboard symlinks..."
    for bin in welcome motd sysinfo welcome-screen; do
        if [ -L "$TARGET_DIR/$bin" ] || [ -f "$TARGET_DIR/$bin" ]; then
            rm -f "$TARGET_DIR/$bin"
            echo -e "  Removed ${TARGET_DIR}/$bin"
        fi
    done

    if [ -t 0 ]; then
        read -p "Do you also want to remove your config (~/.config/welcome) and notes (~/.welcome_notes)? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "${HOME}/.config/welcome"
            rm -f "${HOME}/.welcome_notes"
            echo -e "  Removed configuration and notes."
        fi
    fi
fi

# Remove SSHM binaries
if [ "$REMOVE_SSHM" = true ]; then
    echo -e "\nRemoving sshm symlinks..."
    for bin in sshm sshc ssh-menu; do
        if [ -L "$TARGET_DIR/$bin" ] || [ -f "$TARGET_DIR/$bin" ]; then
            rm -f "$TARGET_DIR/$bin"
            echo -e "  Removed ${TARGET_DIR}/$bin"
        fi
    done
fi

echo -e "\n${GREEN}${BOLD}✓ Uninstallation completed.${RESET}"
echo -e "Note: If you enabled the startup hook in ~/.bashrc or ~/.zshrc, you can remove those lines manually."
