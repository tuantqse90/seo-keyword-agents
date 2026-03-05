# CLAUDE.md — SEO Keyword Agents

## Project Overview

This is a CLI-based SEO intelligence tool that uses Claude as a system prompt agent. The core prompt is in `seo-agent-prompt.txt`.

## Key Files

- `seo-agent-prompt.txt` — The system prompt used by Claude CLI (source of truth)
- `seo-agent-prompt.md` — Prompt documentation with usage instructions
- `setup.sh` — Installation and configuration script
- `docs/examples.md` — Example outputs for each module

## Conventions

- All SEO data must come from real web searches — never fabricate numbers
- Output format is always clean markdown tables + structured reports
- Recommendations must be tagged: [Quick Win], [Medium Effort], [Strategic Investment]
- Vietnamese market context is auto-applied for Vietnamese URLs/topics
- Severity indicators in audits: Critical, Warning, Info

## Modules

1. `/keywords <url_or_topic>` — Keyword research with clusters
2. `/competitor <url>` — Competitive landscape analysis
3. `/content <keyword>` — Production-ready content brief
4. `/audit <url>` — On-page SEO audit with scoring

## Combined Workflows

- `/full <url>` — All 4 modules
- `/strategy <url>` — Keywords + Competitor + Content
- `/fix <url>` — Audit + Quick wins with code

## Rules When Editing This Project

- Keep `seo-agent-prompt.txt` in sync with `seo-agent-prompt.md`
- Test prompt changes by running a sample command before committing
- Maintain backward compatibility with existing alias configurations
