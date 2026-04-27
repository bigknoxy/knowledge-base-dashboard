#!/usr/bin/env sh
set -e

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

KBD_DIR="${HOME}/.local/share/kbd"
KBD_BIN="${HOME}/.local/bin"
PACKAGE_NAME="knowledge-base-dashboard"
GITHUB_REPO="https://github.com/bigknoxy/knowledge-base-dashboard"

install_kbd() {
  DRY_RUN=0
  if [ "$1" = "--dry-run" ]; then
    DRY_RUN=1
    echo "${YELLOW}[DRY RUN] Would execute:${NC}"
  fi

  # 1. Check Python version
  if ! command -v python3 &> /dev/null; then
    echo "${RED}❌ Python 3 not found. Please install Python 3.12 or later.${NC}"
    exit 1
  fi

  PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
  if [ "$(printf '%s\n' "3.12" "$PY_VERSION" | sort -V | head -n1)" != "3.12" ]; then
    echo "${RED}❌ Python 3.12+ required, found $PY_VERSION.${NC}"
    exit 1
  fi
  echo "${GREEN}✓ Python ${PY_VERSION} found${NC}"

  # 2. Check for uv, install if needed
  if ! command -v uv &> /dev/null; then
    echo "${YELLOW}Installing uv package manager...${NC}"
    if [ "$DRY_RUN" -eq 0 ]; then
      curl -fsSL https://astral.sh/uv/install.sh | sh
      export PATH="${HOME}/.local/bin:${PATH}"
    else
      echo "  curl -fsSL https://astral.sh/uv/install.sh | sh"
      echo "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
    fi
  else
    echo "${GREEN}✓ uv found${NC}"
  fi

  # 3. Install kbd via uv pip
  echo "${BLUE}Installing ${PACKAGE_NAME}...${NC}"
  if [ "$DRY_RUN" -eq 0 ]; then
    uv pip install --system "${PACKAGE_NAME}"
  else
    echo "  uv pip install --system ${PACKAGE_NAME}"
  fi

  # 4. Ensure ~/.local/bin is on PATH
  SHELL_RC=""
  if [ -n "${ZSH_VERSION}" ]; then
    SHELL_RC="${HOME}/.zshrc"
  elif [ -n "${BASH_VERSION}" ]; then
    SHELL_RC="${HOME}/.bashrc"
  else
    SHELL_RC="${HOME}/.profile"
  fi

  if [ -f "${SHELL_RC}" ]; then
    if ! grep -q 'export PATH=.*\.local/bin' "${SHELL_RC}"; then
      echo "${BLUE}Adding ${KBD_BIN} to PATH...${NC}"
      if [ "$DRY_RUN" -eq 0 ]; then
        echo "" >> "${SHELL_RC}"
        echo "# Added by kbd installer" >> "${SHELL_RC}"
        echo "export PATH=\"${KBD_BIN}:\${PATH}\"" >> "${SHELL_RC}"
      else
        echo "  echo 'export PATH=\"${KBD_BIN}:\${PATH}\"' >> ${SHELL_RC}"
      fi
    fi
  fi

  # 5. Success message
  if [ "$DRY_RUN" -eq 0 ]; then
    echo ""
    echo "${GREEN}✓ Installation complete!${NC}"
    echo ""
    echo "Quick start:"
    echo "  ${BLUE}source ${SHELL_RC}${NC}      # reload shell"
    echo "  ${BLUE}kbd scan ~/projects${NC}     # scan your repos"
    echo "  ${BLUE}kbd dashboard${NC}           # launch dashboard"
    echo "  ${BLUE}kbd --help${NC}              # see all commands"
    echo ""
    echo "To uninstall:"
    echo "  ${BLUE}curl -fsSL ${GITHUB_REPO}/raw/main/uninstall.sh | sh${NC}"
  fi
}

install_kbd "$@"
