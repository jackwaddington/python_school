# Claude Code Project Configuration

## gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

To install gstack:
```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

Available gstack skills:
- `/plan-ceo-review` — CEO-level plan review
- `/plan-eng-review` — Engineering-level plan review
- `/review` — Code review
- `/ship` — Ship a change
- `/browse` — Web browsing (use this for all web browsing)
- `/qa` — QA a change
- `/qa-only` — QA only (no review)
- `/setup-browser-cookies` — Set up browser cookies
- `/retro` — Retrospective
- `/document-release` — Document a release
