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
INSTALL_SOURCE="${KBD_INSTALL_SOURCE:-git}"
RELEASE_TAG="${KBD_RELEASE_TAG:-v0.1.1}"

install_kbd() {
  DRY_RUN=0
  FORCE_INSTALL=0
  for arg in "$@"; do
    case "$arg" in
      --dry-run) DRY_RUN=1 ;;
      --force) FORCE_INSTALL=1 ;;
      --pypi) INSTALL_SOURCE="pypi" ;;
      *)
        printf '%b\n' "${YELLOW}Unknown argument: $arg${NC}" >&2
        printf '%b\n' "Usage: $0 [--dry-run] [--force] [--pypi]${NC}" >&2
        return 1
        ;;
    esac
  done

  if [ "$DRY_RUN" -eq 1 ]; then
    printf '%b\n' "${YELLOW}[DRY RUN] Would execute:${NC}"
  fi

  # Detect OS (warn if Windows)
  case "$(uname -s)" in
    MINGW*)
      printf '%b\n' "${YELLOW}⚠ Windows detected. This script is optimized for macOS and Linux.${NC}"
      printf '%b\n' "${YELLOW}   Consider using WSL2 or a package manager for Windows support.${NC}"
      ;;
  esac

  # 1. Check Python 3.10+
  if ! command -v python3 > /dev/null 2>&1; then
    printf '%b\n' "${RED}❌ Python 3 not found. Please install Python 3.10 or later.${NC}" >&2
    exit 1
  fi

  PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2> /dev/null || echo "0.0")
  if [ "$(printf '%s\n' "3.10" "$PY_VERSION" | sort -V | head -n1)" != "3.10" ]; then
    printf '%b\n' "${RED}❌ Python 3.10+ required, found $PY_VERSION.${NC}" >&2
    exit 1
  fi
  printf '%b\n' "${GREEN}✓ Python ${PY_VERSION} found${NC}"

  # 2. Check for uv, install if missing
  if ! command -v uv > /dev/null 2>&1; then
    printf '%b\n' "${YELLOW}Installing uv package manager...${NC}"
    if [ "$DRY_RUN" -eq 0 ]; then
      if curl -fsSL https://astral.sh/uv/install.sh | sh > /dev/null 2>&1; then
        export PATH="${HOME}/.local/bin:${PATH}"
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

  # 3. Check if already installed (idempotent)
  if command -v kbd > /dev/null 2>&1 && [ "$FORCE_INSTALL" -eq 0 ]; then
    printf '%b\n' "${GREEN}✓ kbd is already installed at $(command -v kbd)${NC}"
    CURRENT_VERSION=$(kbd version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [ -n "$CURRENT_VERSION" ]; then
      printf '%b\n' "${BLUE}  Version: $CURRENT_VERSION${NC}"
    fi
    printf '%b\n' "${YELLOW}To update, run: kbd update${NC}"
    printf '%b\n' "${YELLOW}To reinstall, run: sh install.sh --force${NC}"
    return 0
  fi

  # 4. Install kbd package (uv tool install handles venv isolation)
  if [ "$FORCE_INSTALL" -eq 1 ]; then
    printf '%b\n' "${BLUE}Reinstalling ${PACKAGE_NAME} (--force)...${NC}"
  else
    printf '%b\n' "${BLUE}Installing ${PACKAGE_NAME}...${NC}"
  fi

  INSTALL_CMD=""
  if [ "$INSTALL_SOURCE" = "git" ]; then
    INSTALL_CMD="uv tool install git+${GITHUB_REPO}.git@${RELEASE_TAG}"
  else
    INSTALL_CMD="uv tool install ${PACKAGE_NAME}"
  fi

  if [ "$FORCE_INSTALL" -eq 1 ]; then
    INSTALL_CMD="$INSTALL_CMD --force"
  fi

  if [ "$DRY_RUN" -eq 0 ]; then
    if ! eval "$INSTALL_CMD" > /dev/null 2>&1; then
      printf '%b\n' "${RED}Failed to install ${PACKAGE_NAME}.${NC}" >&2
      if [ "$INSTALL_SOURCE" = "git" ]; then
        printf '%b\n' "${YELLOW}Tip: Re-run with --pypi to install from PyPI instead of git${NC}" >&2
      fi
      exit 1
    fi
  else
    printf '%b\n' "  $INSTALL_CMD"
  fi

  # 5. Detect shell and update PATH
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

  # 6. Success message
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
