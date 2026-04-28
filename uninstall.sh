#!/usr/bin/env sh
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

KBD_DIR="${HOME}/.local/share/kbd"
KBD_BIN="${HOME}/.local/bin"
PACKAGE_NAME="knowledge-base-dashboard"

log()  { printf "${BLUE}%b${NC}\n" "$1"; }
ok()   { printf "${GREEN}%b${NC}\n" "$1"; }
warn() { printf "${YELLOW}%b${NC}\n" "$1"; }
err()  { printf "${RED}%b${NC}\n" "$1"; }

ask_yes() {
    _prompt="$1"
    if [ -t 0 ]; then
        printf "${YELLOW}%b (y/N) ${NC}" "$_prompt"
        read -r _answer
    else
        _answer="n"
    fi
    [ "$_answer" = "y" ] || [ "$_answer" = "Y" ]
}

uninstall_kbd() {
    FORCE=0
    for arg in "$@"; do
        case "$arg" in
            --force|-y) FORCE=1 ;;
            --help|-h)
                echo "Usage: uninstall.sh [--force] [--help]"
                echo ""
                echo "  --force   Skip confirmation prompts"
                echo "  --help    Show this help"
                exit 0
                ;;
        esac
    done

    log "Uninstalling ${PACKAGE_NAME}..."

    # 1. Remove package via uv
    if command -v uv > /dev/null 2>&1; then
        if uv pip show --system "${PACKAGE_NAME}" > /dev/null 2>&1; then
            log "Removing Python package..."
            uv pip uninstall --system "${PACKAGE_NAME}" 2>/dev/null || \
                uv pip uninstall -y "${PACKAGE_NAME}" 2>/dev/null || true
            ok "✓ Removed Python package"
        else
            ok "✓ Package not installed via uv — skipping"
        fi
    else
        warn "⚠ uv not found — cannot uninstall Python package automatically"
    fi

    # 2. Remove kbd binary/symlink
    # Check both ~/.local/bin and /usr/local/bin (where --break-system-packages installs)
    _removed=0
    if [ -e "${KBD_BIN}/kbd" ] || [ -L "${KBD_BIN}/kbd" ]; then
        rm -f "${KBD_BIN}/kbd"
        ok "✓ Removed ${KBD_BIN}/kbd"
        _removed=1
    fi
    if [ -e "/usr/local/bin/kbd" ] || [ -L "/usr/local/bin/kbd" ]; then
        rm -f /usr/local/bin/kbd
        ok "✓ Removed /usr/local/bin/kbd"
        _removed=1
    fi
    if [ "$_removed" -eq 0 ]; then
        ok "✓ No kbd binary found — skipping"
    fi

    # 3. Optional data cleanup
    echo ""
    warn "Local data cleanup (optional):"

    if [ -d "${KBD_DIR}" ]; then
        if [ "$FORCE" -eq 1 ] || ask_yes "Remove ${KBD_DIR}/ ?"; then
            rm -rf "${KBD_DIR}"
            ok "✓ Removed ${KBD_DIR}/"
        fi
    else
        ok "✓ No ${KBD_DIR}/ directory — skipping"
    fi

    if [ -f "kbd.db" ]; then
        if [ "$FORCE" -eq 1 ] || ask_yes "Remove kbd.db from current directory?"; then
            rm -f kbd.db
            ok "✓ Removed kbd.db"
        fi
    fi

    if [ -f "config.toml" ]; then
        if [ "$FORCE" -eq 1 ] || ask_yes "Remove config.toml from current directory?"; then
            rm -f config.toml
            ok "✓ Removed config.toml"
        fi
    fi

    if [ -d "${HOME}/.config/kbd" ]; then
        if [ "$FORCE" -eq 1 ] || ask_yes "Remove ~/.config/kbd/ (all user config)?"; then
            rm -rf "${HOME}/.config/kbd"
            ok "✓ Removed ~/.config/kbd/"
        fi
    else
        ok "✓ No ~/.config/kbd/ directory — skipping"
    fi

    echo ""
    ok "✓ Uninstall complete"
    echo "To reinstall:"
    echo "  ${BLUE}curl -fsSL https://github.com/bigknoxy/knowledge-base-dashboard/raw/refs/heads/main/install.sh | sh${NC}"
}

uninstall_kbd "$@"
