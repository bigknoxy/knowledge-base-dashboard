#!/usr/bin/env sh
set -e

# Color codes (disabled on Windows)
if [ -z "$TERM" ] || [ "$TERM" = "dumb" ]; then
  BLUE='' GREEN='' YELLOW='' RED='' NC=''
else
  BLUE='\033[0;34m' GREEN='\033[0;32m' YELLOW='\033[1;33m' RED='\033[0;31m' NC='\033[0m'
fi

KBD_BIN="${HOME}/.local/bin"
PACKAGE_NAME="knowledge-base-dashboard"
GITHUB_REPO="https://github.com/bigknoxy/knowledge-base-dashboard"

install_kbd() {
  DRY_RUN=0
  if [ "$1" = "--dry-run" ]; then
    DRY_RUN=1
    printf '%b\n' "${YELLOW}[DRY RUN] Would execute:${NC}"
  fi

  # Detect OS (warn if Windows)
  if [ "$(uname -s | cut -c1-10)" = "MINGW32_NT" ] || [ "$(uname -s | cut -c1-10)" = "MINGW64_NT" ]; then
    printf '%b\n' "${YELLOW}⚠ Windows detected. This script is optimized for macOS and Linux.${NC}"
    printf '%b\n' "${YELLOW}   Consider using WSL2 or a package manager for Windows support.${NC}"
  fi

  # 1. Check Python 3.12+
  if ! command -v python3 > /dev/null 2>&1; then
    printf '%b\n' "${RED}❌ Python 3 not found. Please install Python 3.12 or later.${NC}" >&2
    exit 1
  fi

  PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2> /dev/null || echo "0.0")
  if [ "$(printf '%s\n' "3.12" "$PY_VERSION" | sort -V | head -n1)" != "3.12" ]; then
    printf '%b\n' "${RED}❌ Python 3.12+ required, found $PY_VERSION.${NC}" >&2
    exit 1
  fi
  printf '%b\n' "${GREEN}✓ Python ${PY_VERSION} found${NC}"

  # 2. Check for uv, install if missing
  UV_INSTALLED=0
  if ! command -v uv > /dev/null 2>&1; then
    printf '%b\n' "${YELLOW}Installing uv package manager...${NC}"
    if [ "$DRY_RUN" -eq 0 ]; then
      if curl -fsSL https://astral.sh/uv/install.sh | sh > /dev/null 2>&1; then
        export PATH="${HOME}/.local/bin:${PATH}"
        UV_INSTALLED=1
      else
        printf '%b\n' "${RED}❌ Failed to install uv. Check internet connection.${NC}" >&2
        exit 1
      fi
    else
      printf '%b\n' "  curl -fsSL https://astral.sh/uv/install.sh | sh"
      printf '%b\n' "  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
    fi
  else
    printf '%b\n' "${GREEN}✓ uv found${NC}"
  fi

  # 3. Install kbd package
  printf '%b\n' "${BLUE}Installing ${PACKAGE_NAME}...${NC}"
  if [ "$DRY_RUN" -eq 0 ]; then
    if ! uv pip install --system "${PACKAGE_NAME}" > /dev/null 2>&1; then
      printf '%b\n' "${RED}❌ Failed to install ${PACKAGE_NAME}. Check PyPI availability.${NC}" >&2
      exit 1
    fi
  else
    printf '%b\n' "  uv pip install --system ${PACKAGE_NAME}"
  fi

  # 4. Detect shell and update PATH
  SHELL_RC=""
  if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="${HOME}/.zshrc"
  elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="${HOME}/.bashrc"
  else
    # Fallback: check SHELL env var or use .profile
    case "$SHELL" in
      *zsh) SHELL_RC="${HOME}/.zshrc" ;;
      *bash) SHELL_RC="${HOME}/.bashrc" ;;
      *fish) SHELL_RC="${HOME}/.config/fish/config.fish" ;;
      *) SHELL_RC="${HOME}/.profile" ;;
    esac
  fi

  if [ "$DRY_RUN" -eq 0 ]; then
    if [ -w "$SHELL_RC" ] 2> /dev/null || touch "$SHELL_RC" 2> /dev/null; then
      if ! grep -q 'export PATH=.*\.local/bin' "$SHELL_RC" 2> /dev/null; then
        printf '%b\n' "${BLUE}Adding ${KBD_BIN} to PATH...${NC}"
        {
          echo ""
          echo "# Added by kbd installer"
          echo "export PATH=\"${KBD_BIN}:\${PATH}\""
        } >> "$SHELL_RC"
      fi
    else
      printf '%b\n' "${YELLOW}⚠ Could not write to ${SHELL_RC}. Add manually:${NC}"
      printf '%b\n' "  export PATH=\"${KBD_BIN}:\${PATH}\""
    fi
  else
    printf '%b\n' "  # Ensure ${KBD_BIN} is on PATH in ${SHELL_RC}"
  fi

  # 5. Success message
  if [ "$DRY_RUN" -eq 0 ]; then
    printf '\n%b\n' "${GREEN}✓ Installation complete!${NC}"
    printf '%b\n' ""
    printf '%b\n' "Quick start:"
    printf '%b\n' "  ${BLUE}source ${SHELL_RC}${NC}      # reload shell"
    printf '%b\n' "  ${BLUE}kbd init${NC}               # initialize config"
    printf '%b\n' "  ${BLUE}kbd scan ~/projects${NC}    # scan your repos"
    printf '%b\n' "  ${BLUE}kbd dashboard${NC}          # launch dashboard"
    printf '%b\n' ""
    printf '%b\n' "To uninstall:"
    printf '%b\n' "  ${BLUE}curl -fsSL ${GITHUB_REPO}/raw/main/uninstall.sh | sh${NC}"
  else
    printf '\n%b\n' "${GREEN}✓ Dry run complete. No changes made.${NC}"
  fi
}

install_kbd "$@"
