# Changelog

All notable changes to pal-steamline are documented here.

This project is a fork of [PAL MCP Server](https://github.com/ppl-ai/pal-mcp-server) by Fahad Gilani (upstream v9.8.2). The version history below covers changes made in this fork only. For upstream history, see `README-dep.md`.

---

## [1.0.0] — 2026-04-11

Initial fork release. pal-steamline is a stripped-down, Claude Code–focused variant of PAL MCP Server. The goal is a smaller tool surface, deterministic model routing, and a dual-provider setup (Custom API primary + OpenRouter secondary).

### Removed

**Tools (9 removed):**
- `clink` — CLI-to-CLI bridge tool deleted; not needed in Claude Code context
- `planner` — interactive sequential planning tool deleted
- `analyze` — code assessment tool deleted
- `secaudit` — security audit tool deleted
- `tracer` — code tracing and dependency mapping tool deleted
- `docgen` — documentation generation tool deleted
- `precommit` — pre-commit validation tool deleted
- `testgen` — test generation tool deleted
- `challenge` — adversarial debate tool deleted

**Tool consolidation:**
- `review` tool (formerly `codereview`) — review-only mode (refactor mode removed)

**Model routing:**
- Auto-mode intelligence removed — dynamic model selection engine stripped out
- `DEFAULT_MODEL` fallback hardcoded to `mimo`; no runtime model discovery

**Tests:**
- OpenAI HTTP cassette integration suite deleted (`tests/openai_cassettes/`, 5 consumer test files, cassette infrastructure)
- Gemini SDK replay integration suite deleted (`tests/gemini_cassettes/`, 3 consumer test files)
- 14 stale simulator tests removed (tested removed tools or upstream-only paths)
- 21 pre-existing test failures fixed (stale assertions against removed features)

**Docs:**
- Upstream docs referencing removed tools and providers pruned from `docs/`
- `README.md` replaced with fork-specific document; upstream README archived as `README-dep.md`

**CI/CD:**
- `semantic-release.yml` workflow removed (auto-published releases on every push to main)
- `semantic-pr.yml` workflow removed (conventional commit enforcement for external PRs)
- `docker-pr.yml` workflow removed (Docker build per PR)
- `docker-release.yml` workflow removed (publishes to ghcr.io on release)
- `FUNDING.yml` removed (upstream maintainer's GitHub Sponsors link)
- `ISSUE_TEMPLATE/config.yml` removed (all links pointed to upstream repo)
- `ISSUE_TEMPLATE/tool_addition.yml` removed (proposes adding tools this fork removes)

### Added

**Model aliases (4 total):**
- `mimo` — default; routes to `xiaomi/mimo-v2.5-pro` via Custom API
- `gemini` — routes to `google/gemini-3.1-pro-preview` via OpenRouter; used as expert escalation model
- `gpt` — routes to `openai/gpt-5.4` via OpenRouter

**Expert escalation:**
- `EXPERT_MODEL` config added — workflow tools (`thinkdeep`, `review`, `consensus`) run a two-pass analysis: primary model does the work, `EXPERT_MODEL` (`gemini` by default) validates

**Configuration:**
- `DEFAULT_MODEL=mimo`, `EXPERT_MODEL=gemini` as fork defaults
- `docker-compose.yml` default updated from `auto` to `mimo`
- `*.code` added to `.gitignore` to prevent tracking generated session output files

### Changed

- Version reset from upstream `9.8.2` to `1.0.0`
- `config.py` `DEFAULT_MODEL` fallback changed from `gemini-2.5-flash` to `mimo`
- CLAUDE.md updated with fork-specific commands, model aliases, and tool picker guidance
- `AGENTS.md` example test command updated to reference a valid test file

---

*Forked from PAL MCP Server v9.8.2 — upstream repository: https://github.com/ppl-ai/pal-mcp-server*
