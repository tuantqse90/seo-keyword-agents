#!/bin/bash

# SEO Keyword Agents — Setup Script
# Configures Claude CLI with the SEO agent system prompt

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/seo-agent-prompt.txt"
SHELL_RC=""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "  SEO Keyword Agents — Setup"
echo "========================================="
echo ""

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: Claude CLI is not installed.${NC}"
    echo "Install it first: https://docs.anthropic.com/en/docs/claude-cli"
    exit 1
fi

echo -e "${GREEN}Claude CLI found.${NC}"

# Check prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}Error: seo-agent-prompt.txt not found at $PROMPT_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}Prompt file found.${NC}"
echo ""

# Detect shell
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_RC="$HOME/.bash_profile"
fi

# Ask user for setup method
echo "Choose setup method:"
echo ""
echo "  1) Set as default system prompt (affects all Claude sessions)"
echo "  2) Create 'seo' shell alias (recommended)"
echo "  3) Both"
echo ""
read -p "Enter choice [1/2/3]: " choice

case $choice in
    1)
        echo ""
        echo "Setting system prompt..."
        claude config set systemPrompt "$(cat "$PROMPT_FILE")"
        echo -e "${GREEN}System prompt configured.${NC}"
        echo ""
        echo "Usage:"
        echo "  claude \"/keywords example.com\""
        echo "  claude \"/audit example.com\""
        ;;
    2)
        if [ -z "$SHELL_RC" ]; then
            echo -e "${RED}Could not detect shell config file.${NC}"
            echo "Add this alias manually to your shell config:"
            echo ""
            echo "  alias seo='claude --system-prompt \"\$(cat $PROMPT_FILE)\"'"
            exit 1
        fi
        echo ""
        # Remove old alias if exists
        if grep -q "alias seo=" "$SHELL_RC" 2>/dev/null; then
            sed -i.bak "/alias seo=/d" "$SHELL_RC"
            echo -e "${YELLOW}Removed existing 'seo' alias.${NC}"
        fi
        echo "alias seo='claude --system-prompt \"\$(cat $PROMPT_FILE)\"'" >> "$SHELL_RC"
        echo -e "${GREEN}Alias 'seo' added to $SHELL_RC${NC}"
        echo ""
        echo "Run this to activate:"
        echo "  source $SHELL_RC"
        echo ""
        echo "Usage:"
        echo "  seo \"/keywords example.com\""
        echo "  seo \"/audit example.com\""
        echo "  seo \"/full nullshift.sh\""
        ;;
    3)
        echo ""
        echo "Setting system prompt..."
        claude config set systemPrompt "$(cat "$PROMPT_FILE")"
        echo -e "${GREEN}System prompt configured.${NC}"

        if [ -n "$SHELL_RC" ]; then
            if grep -q "alias seo=" "$SHELL_RC" 2>/dev/null; then
                sed -i.bak "/alias seo=/d" "$SHELL_RC"
            fi
            echo "alias seo='claude --system-prompt \"\$(cat $PROMPT_FILE)\"'" >> "$SHELL_RC"
            echo -e "${GREEN}Alias 'seo' added to $SHELL_RC${NC}"
            echo ""
            echo "Run: source $SHELL_RC"
        fi
        echo ""
        echo "Usage:"
        echo "  seo \"/keywords example.com\""
        echo "  claude \"/audit example.com\""
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo -e "  ${GREEN}Setup complete!${NC}"
echo "========================================="
echo ""
echo "Quick start commands:"
echo "  /keywords <url>       Keyword research"
echo "  /competitor <url>     Competitor analysis"
echo "  /content <keyword>    Content brief"
echo "  /audit <url>          On-page audit"
echo "  /full <url>           All modules"
echo "  /strategy <url>       Keywords + Competitor + Content"
echo "  /fix <url>            Audit + Quick wins"
