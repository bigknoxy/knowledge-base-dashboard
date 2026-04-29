#!/usr/bin/env sh
set -e

# Color codes (disabled on Windows/non-interactive)
if [ -z "$TERM" ] || [ "$TERM" = "dumb" ] || [ ! -t 0 ]; then
  BLUE='' GREEN='' YELLOW='' RED='' NC=''
else
  BLUE='\033[0;34m' GREEN='\033[0;32m' YELLOW='\033[1;33m' RED='\033[0;31m' NC='\033[0m'
fi

KBD_BIN="${HOME}/.local/bin/kbd"
PACKAGE_NAME="knowledge-base-dashboard"

# POSIX-compatible read function (works in non-interactive shells)
prompt_yes_no() {
  if [ ! -t 0 ]; then
    echo "n"
    return
  fi
  printf '%s' "$1 (y/N) "
  read -r answer < /dev/tty
  echo "$answer"
}

uninstall_kbd() {
  printf '%b\n' "${BLUE}Uninstalling ${PACKAGE_NAME}...${NC}"

  # 1. Remove binary
  if [ -e "$KBD_BIN" ] || [ -L "$KBD_BIN" ]; then
    rm -f "$KBD_BIN" 2> /dev/null || true
    printf '%b\n' "${GREEN}✓ Removed $KBD_BIN${NC}"
  fi

  # 2. Remove Python package
  if command -v uv > /dev/null 2>&1; then
    printf '%b\n' "${BLUE}Removing Python package...${NC}"
    uv pip uninstall -y "$PACKAGE_NAME" > /dev/null 2>&1 || true
    printf '%b\n' "${GREEN}✓ Removed Python package${NC}"
  fi

  # 3. Interactive cleanup (skip if non-interactive)
  printf '\n%b\n' "${YELLOW}Local data cleanup (optional):${NC}"

  answer=$(prompt_yes_no "Remove ~/.local/share/kbd/?")
  if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -rf "${HOME}/.local/share/kbd" 2> /dev/null || true
    printf '%b\n' "${GREEN}✓ Removed ~/.local/share/kbd/${NC}"
  fi

  answer=$(prompt_yes_no "Remove local kbd.db and config.toml?")
  if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -f kbd.db config.toml 2> /dev/null || true
    printf '%b\n' "${GREEN}✓ Removed local files${NC}"
  fi

  answer=$(prompt_yes_no "Remove ~/.config/kbd/ (all config)?")
  if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm -rf "${HOME}/.config/kbd" 2> /dev/null || true
    printf '%b\n' "${GREEN}✓ Removed ~/.config/kbd/${NC}"
  fi

  printf '\n%b\n' "${GREEN}✓ Uninstall complete${NC}"
  printf '%b\n' "To reinstall:"
  printf '%b\n' "  ${BLUE}curl -fsSL https://github.com/bigknoxy/knowledge-base-dashboard/raw/main/install.sh | sh${NC}"
}

uninstall_kbd "$@"
