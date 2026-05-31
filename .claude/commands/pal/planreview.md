---
description: Send the most recent Claude Code plan to a PAL model for critical review.
allowed-tools: Bash(ls *), Bash(find ~/.claude/plans *), Read
---

## Locate the plan

If `$ARGUMENTS` is non-empty, treat it as a plan filename (with or without `.md`) inside `~/.claude/plans/` and read that file. Otherwise find the most recently modified plan:

```
ls -t ~/.claude/plans/*.md | head -1
```

Read the full plan with the Read tool.

## Send to PAL for review

Call `mcp__pal__chat` with:
- `model`: `mimo` (default) — override if user specifies one
- `prompt`: the full plan text, prefixed with this instruction:

```
You are reviewing a software implementation plan. Your job is feedback only — do not implement anything.

Critically review this plan covering:
1. Goal clarity — Is the problem and desired outcome stated plainly? Any ambiguity?
2. Scope — Too much, too little, or drifting from the stated goal?
3. Risks & blast radius — Irreversible steps, shared-system changes, missing rollback paths.
4. Sequencing — Steps in the right order? Hidden dependencies?
5. Edge cases & failure modes — What's unhandled? What assumptions are load-bearing?
6. Testability — Can the outcome actually be verified?
7. Reuse — Does the plan propose new code where existing utilities would serve?

End with a numbered list of concrete recommendations, ordered by importance.

PLAN:
<plan content here>
```

Return the PAL model's response to the user.
