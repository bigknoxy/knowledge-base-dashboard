#!/usr/bin/env sh
set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

KBD_BIN="${HOME}/.local/bin"
PACKAGE_NAME="knowledge-base-dashboard"
GITHUB_REPO="https://github.com/bigknoxy/knowledge-base-dashboard"

log()  { printf "${BLUE}%b${NC}\n" "$1"; }
ok()   { printf "${GREEN}%b${NC}\n" "$1"; }
warn() { printf "${YELLOW}%b${NC}\n" "$1"; }
err()  { printf "${RED}%b${NC}\n" "$1"; }

version_gte() {
    # Returns true if user version ($1) >= required ($2)
    # Using sort -V: if required is smallest, user has required or better
    _min="$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n1)"
    [ "$_min" = "$2" ]
}

detect_shell_rc() {
    if [ -n "${ZSH_VERSION:-}" ]; then
        echo "${HOME}/.zshrc"
    elif [ -n "${BASH_VERSION:-}" ]; then
        echo "${HOME}/.bashrc"
    else
        echo "${HOME}/.profile"
    fi
}

ensure_path_entry() {
    _rc="$1"
    _dir="$2"

    if [ ! -f "$_rc" ]; then
        return 0
    fi

    if grep -q "^export PATH=.*${_dir}" "$_rc" 2>/dev/null; then
        return 0
    fi

    if grep -q ":${_dir}:" "$_rc" 2>/dev/null || grep -q ":${_dir}\"" "$_rc" 2>/dev/null; then
        return 0
    fi

    log "Adding ${_dir} to PATH in ${_rc}..."
    # shellcheck disable=SC2016
    printf '\n# Added by kbd installer\nexport PATH="%s:$PATH"\n' "$_dir" >> "$_rc"
}

install_kbd() {
    DRY_RUN=0
    SKIP_PY_CHECK=0
    for arg in "$@"; do
        case "$arg" in
            --dry-run)   DRY_RUN=1; echo "${YELLOW}[DRY RUN] Would execute:${NC}" ;;
            --skip-py)   SKIP_PY_CHECK=1 ;;
            --help|-h)
                echo "Usage: install.sh [--dry-run] [--skip-py] [--help]"
                echo ""
                echo "  --dry-run   Print what would be done without doing it"
                echo "  --skip-py   Skip Python version check"
                echo "  --help      Show this help"
                exit 0
                ;;
        esac
    done

    # ── 1. Python check ──────────────────────────────────────────────
    if [ "$SKIP_PY_CHECK" -eq 0 ]; then
        if ! command -v python3 > /dev/null 2>&1; then
            err "❌ Python 3 not found. Please install Python 3.12 or later."
            err "   https://www.python.org/downloads/"
            exit 1
        fi

        PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        PY_MAJOR_MINOR=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

        if ! version_gte "$PY_MAJOR_MINOR" "3.12"; then
            err "❌ Python 3.12+ required, found ${PY_VERSION}."
            err "   https://www.python.org/downloads/"
            exit 1
        fi
        ok "✓ Python ${PY_VERSION} found"
    fi

    # ── 2. uv check / install ────────────────────────────────────────
    if ! command -v uv > /dev/null 2>&1; then
        warn "uv not found — installing..."
        if [ "$DRY_RUN" -eq 0 ]; then
            curl -fsSL https://astral.sh/uv/install.sh | sh
            export PATH="${HOME}/.local/bin:${PATH}"
        else
            echo "  curl -fsSL https://astral.sh/uv/install.sh | sh"
            echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
        fi

        if ! command -v uv > /dev/null 2>&1; then
            export PATH="${HOME}/.local/bin:${PATH}"
        fi

        if ! command -v uv > /dev/null 2>&1; then
            err "❌ uv installation failed. Please install manually:"
            err "   curl -fsSL https://astral.sh/uv/install.sh | sh"
            exit 1
        fi
    fi
    ok "✓ uv found"

    # ── 3. Install / upgrade package ─────────────────────────────────
    ALREADY_INSTALLED=0
    if command -v kbd > /dev/null 2>&1; then
        ALREADY_INSTALLED=1
    fi

    # Install from GitHub (not on PyPI)
    INSTALL_URL="git+${GITHUB_REPO}.git"

    if [ "$DRY_RUN" -eq 0 ]; then
        if [ "$ALREADY_INSTALLED" -eq 1 ]; then
            log "Updating ${PACKAGE_NAME}..."
        else
            log "Installing ${PACKAGE_NAME}..."
        fi
        uv pip install --system "${INSTALL_URL}" 2>&1 || {
            err "❌ Installation failed. Trying with --break-system-packages..."
            uv pip install --system --break-system-packages "${INSTALL_URL}" 2>&1 || {
                err "❌ Installation failed. Try running:"
                err "   uv pip install --system ${INSTALL_URL}"
                exit 1
            }
        }
    else
        echo "  uv pip install --system ${INSTALL_URL}"
    fi

    if [ "$ALREADY_INSTALLED" -eq 1 ]; then
        ok "✓ ${PACKAGE_NAME} updated"
    else
        ok "✓ ${PACKAGE_NAME} installed"
    fi

    # ── 4. Ensure ~/.local/bin on PATH ───────────────────────────────
    SHELL_RC=$(detect_shell_rc)

    if [ "$DRY_RUN" -eq 0 ]; then
        ensure_path_entry "$SHELL_RC" "$KBD_BIN"
    else
        echo "  ensure_path_entry ${SHELL_RC} ${KBD_BIN}"
    fi

    case ":${PATH}:" in
        *":${KBD_BIN}:"*) ;;
        *) export PATH="${KBD_BIN}:${PATH}" ;;
    esac

    # ── 5. Verify installation ───────────────────────────────────────
    if [ "$DRY_RUN" -eq 0 ]; then
        if command -v kbd > /dev/null 2>&1; then
            INSTALLED_VER=$(kbd --version 2>/dev/null || echo "unknown")
            ok "✓ kbd ${INSTALLED_VER} is on PATH"
        else
            warn "⚠ kbd installed but not yet on PATH."
            warn "  Run: source ${SHELL_RC}"
        fi
    fi

    # ── 6. Success ───────────────────────────────────────────────────
    echo ""
    if [ "$DRY_RUN" -eq 0 ]; then
        ok "✓ Installation complete!"
    else
        ok "✓ Dry run complete — no changes made."
    fi
    echo ""
    echo "Quick start:"
    echo "  ${BLUE}source ${SHELL_RC}${NC}      # reload shell"
    echo "  ${BLUE}kbd scan ~/projects${NC}     # scan your repos"
    echo "  ${BLUE}kbd dashboard${NC}           # launch dashboard"
    echo "  ${BLUE}kbd --help${NC}              # see all commands"
    echo ""
    echo "To uninstall:"
    echo "  ${BLUE}curl -fsSL ${GITHUB_REPO}/raw/refs/heads/main/uninstall.sh | sh${NC}"
    echo ""
    echo "Re-run anytime to update — this script is idempotent."
}

install_kbd "$@"
