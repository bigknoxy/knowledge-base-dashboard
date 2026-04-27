#!/usr/bin/env sh
set -e

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

KBD_BIN="${HOME}/.local/bin/kbd"
PACKAGE_NAME="knowledge-base-dashboard"

uninstall_kbd() {
  echo "${BLUE}Uninstalling ${PACKAGE_NAME}...${NC}"

  # 1. Remove kbd symlink/binary
  if [ -e "${KBD_BIN}" ] || [ -L "${KBD_BIN}" ]; then
    rm -f "${KBD_BIN}"
    echo "${GREEN}✓ Removed ${KBD_BIN}${NC}"
  fi

  # 2. Remove package via uv if available
  if command -v uv &> /dev/null; then
    echo "${BLUE}Removing Python package...${NC}"
    uv pip uninstall -y "${PACKAGE_NAME}" || true
    echo "${GREEN}✓ Removed Python package${NC}"
  fi

  # 3. Offer to remove local data
  echo ""
  echo "${YELLOW}Local data cleanup (optional):${NC}"

  read -p "Remove ~/.local/share/kbd/ ? (y/N) " -r
  if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    rm -rf "${HOME}/.local/share/kbd"
    echo "${GREEN}✓ Removed ~/.local/share/kbd/${NC}"
  fi

  read -p "Remove kbd.db and config.toml from current directory ? (y/N) " -r
  if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    rm -f kbd.db config.toml
    echo "${GREEN}✓ Removed local kbd.db and config.toml${NC}"
  fi

  # 4. Ask about config cleanup
  read -p "Remove ~/.config/kbd/ (all user config)? (y/N) " -r
  if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
    rm -rf "${HOME}/.config/kbd"
    echo "${GREEN}✓ Removed ~/.config/kbd/${NC}"
  fi

  echo ""
  echo "${GREEN}✓ Uninstall complete${NC}"
  echo "To reinstall:"
  echo "  ${BLUE}curl -fsSL https://github.com/bigknoxy/knowledge-base-dashboard/raw/main/install.sh | sh${NC}"
}

uninstall_kbd "$@"
