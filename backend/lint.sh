#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Romulus Backend Linting & Formatting${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Parse arguments
FIX_MODE=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./lint.sh [--fix] [--check]"
            echo "  --fix    Automatically fix all auto-fixable issues"
            echo "  --check  Only check, don't fix anything (CI mode)"
            exit 1
            ;;
    esac
done

# Step 1: Ruff Check (Linting)
echo -e "${YELLOW}[1/3] Running Ruff linter...${NC}"
echo ""

if [ "$CHECK_ONLY" = true ]; then
    # CI mode: just check
    if uv run ruff check . --output-format=concise; then
        echo -e "${GREEN}✓ No linting issues found${NC}"
        LINT_STATUS=0
    else
        echo -e "${RED}✗ Linting issues found${NC}"
        LINT_STATUS=1
    fi
elif [ "$FIX_MODE" = true ]; then
    # Fix mode: automatically fix what we can
    if uv run ruff check . --fix --output-format=concise; then
        echo -e "${GREEN}✓ All auto-fixable linting issues corrected${NC}"
        LINT_STATUS=0
    else
        echo -e "${YELLOW}⚠ Some issues require manual attention${NC}"
        LINT_STATUS=1
    fi
else
    # Default: show issues without fixing
    if uv run ruff check . --output-format=full; then
        echo -e "${GREEN}✓ No linting issues found${NC}"
        LINT_STATUS=0
    else
        echo -e "${YELLOW}⚠ Linting issues found (run with --fix to auto-fix)${NC}"
        LINT_STATUS=1
    fi
fi

echo ""

# Step 2: Ruff Format (Code Formatting)
echo -e "${YELLOW}[2/3] Running Ruff formatter...${NC}"
echo ""

if [ "$CHECK_ONLY" = true ]; then
    # CI mode: just check formatting
    if uv run ruff format . --check --diff; then
        echo -e "${GREEN}✓ Code is properly formatted${NC}"
        FORMAT_STATUS=0
    else
        echo -e "${RED}✗ Code formatting issues found${NC}"
        FORMAT_STATUS=1
    fi
else
    # Fix mode or default: format the code
    if uv run ruff format .; then
        echo -e "${GREEN}✓ Code formatted successfully${NC}"
        FORMAT_STATUS=0
    else
        echo -e "${RED}✗ Formatting failed${NC}"
        FORMAT_STATUS=1
    fi
fi

echo ""

# Step 3: Summary
echo -e "${YELLOW}[3/3] Summary${NC}"
echo ""

TOTAL_STATUS=$((LINT_STATUS + FORMAT_STATUS))

if [ $TOTAL_STATUS -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ✓ All checks passed!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [ "$CHECK_ONLY" = true ]; then
        echo -e "${RED}  ✗ Checks failed! Please run './lint.sh --fix' to auto-fix issues.${NC}"
    else
        echo -e "${RED}  ✗ Some issues require manual attention${NC}"
        echo -e "${YELLOW}  Review the output above for details${NC}"
    fi
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Show helpful commands
    echo ""
    echo -e "${BLUE}Helpful commands:${NC}"
    echo "  ./lint.sh           - Check for issues (don't fix)"
    echo "  ./lint.sh --fix     - Auto-fix all fixable issues"
    echo "  ./lint.sh --check   - CI mode (check only, fail on issues)"
    echo ""

    exit $TOTAL_STATUS
fi
