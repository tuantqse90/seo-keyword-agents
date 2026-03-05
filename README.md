# SEO Keyword Agents

CLI-based SEO intelligence tool powered by Claude. Provides keyword research, competitor analysis, content briefs, and on-page audits — all from your terminal.

## Features

| Module | Command | Description |
|--------|---------|-------------|
| Keyword Research | `/keywords <url_or_topic>` | 15-20 keyword suggestions with volume, difficulty, intent, CPC, and opportunity scores |
| Competitor Analysis | `/competitor <url>` | Identify competitors, keyword gaps, content gaps, strategic recommendations |
| Content Brief | `/content <keyword>` | Production-ready brief with outline, LSI keywords, E-E-A-T signals |
| On-Page Audit | `/audit <url>` | SEO score (0-100), categorized issues, quick wins, technical checklist |

### Combined Workflows

| Workflow | Command | What it does |
|----------|---------|--------------|
| Full Report | `/full <url>` | All 4 modules sequentially |
| Strategy | `/strategy <url>` | Keywords + Competitor + Content brief for top opportunity |
| Quick Fix | `/fix <url>` | Audit + Quick wins with implementation code |

## Prerequisites

- [Claude CLI](https://docs.anthropic.com/en/docs/claude-cli) installed and authenticated
- Active Anthropic API key or Claude Pro/Max subscription

## Installation

### Quick Setup

```bash
git clone <repo-url> seo-keyword-agents
cd seo-keyword-agents
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
# Option 1: Set as system prompt
claude config set systemPrompt "$(cat seo-agent-prompt.txt)"

# Option 2: Use inline per session
claude --system-prompt "$(cat seo-agent-prompt.txt)"

# Option 3: Create a shell alias
echo 'alias seo='\''claude --system-prompt "$(cat ~/path/to/seo-agent-prompt.txt)"'\''' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Keyword Research

```bash
seo "/keywords nullshift.sh"
seo "/keywords 'best AI tools 2026'"
seo "/keywords 'thiet ke web da nang'"
```

Output includes:
- Keyword table organized by cluster (head terms, long-tail, question-based)
- Golden keywords highlighted (high volume + low difficulty + commercial intent)
- Content silo strategy suggestions

### Competitor Analysis

```bash
seo "/competitor nullshift.sh"
seo "/competitor example.com"
```

Output includes:
- 3-5 competitor cards with traffic, DA, top keywords
- Keyword gap matrix
- Content gap analysis
- Prioritized action items (impact vs effort)

### Content Brief

```bash
seo "/content 'privacy-first AI agent'"
seo "/content 'best CRM software' --url example.com"
```

Output includes:
- Title tag + meta description (optimized length)
- Full H2/H3 content outline
- 15-20 LSI/semantic keywords
- Featured snippet optimization strategy
- E-E-A-T signal recommendations

### On-Page Audit

```bash
seo "/audit example.com"
seo "/audit nullshift.sh"
```

Output includes:
- SEO score (0-100) with letter grade
- Issues by severity (Critical / Warning / Info)
- Top 5 quick wins
- Technical checklist (robots.txt, sitemap, canonical, schema)

### Combined Workflows

```bash
# Full comprehensive report
seo "/full nullshift.sh"

# Strategy: keywords + competitor + content brief
seo "/strategy example.com"

# Quick fixes with code snippets
seo "/fix example.com"
```

## Vietnamese Market Support

When analyzing Vietnamese websites or topics, the agent automatically:
- Considers Google.com.vn ranking factors
- Adapts to Vietnamese search behavior patterns
- Includes local SEO factors
- Handles Vietnamese diacritics and keyword variations

```bash
seo "/keywords 'thiet ke website'"
seo "/audit tiki.vn"
seo "/full shopee.vn"
```

## Output Format

All outputs use clean markdown optimized for terminal readability:
- Tables for structured data (keywords, competitors)
- Headers and bullet points for reports
- Code snippets for technical fixes
- Severity indicators for audit issues

## Project Structure

```
seo-keyword-agents/
├── README.md                  # This file
├── CLAUDE.md                  # Claude Code project rules
├── seo-agent-prompt.md        # Prompt documentation (source)
├── seo-agent-prompt.txt       # Clean prompt file (for CLI use)
├── setup.sh                   # Installation script
└── docs/
    └── examples.md            # Example outputs for each module
```

## Tips

1. **Start with `/keywords`** to identify opportunities, then chain to `/content` for the best keyword
2. **Use `/full`** for initial site assessment — it covers everything
3. **Run `/fix`** for quick, actionable improvements with code you can copy-paste
4. **For Vietnamese sites**, the agent auto-detects and adjusts its analysis
5. **Chain commands** in a conversation for contextual analysis — the agent remembers previous results

## License

MIT
