# Global CLAUDE.md

## Output format
- for plans, reports, design docs, and anything benefiting from diagrams, styling, or embedded images, prefer HTML over Markdown
- for conventional files (README, CONTRIBUTING, LICENSE, CHANGELOG, etc.) use the ecosystem default

## Diagnostics
- IMPORTANT: pursue root cause before proposing a fix; never propose a manual workaround before identifying the underlying cause
- if a fix doesn't resolve the symptom, dig deeper instead of layering patches
- verify the fix addresses the reported behavior, not just that the error went away
- for system/boot/network/regression bugs, write a root-cause hypothesis first (see ~/.config/claude/rules/diagnostics.md)

## Trust & verification
- IMPORTANT: don't present plausible-sounding details as facts; verify file paths, flags, function and library behavior by reading code or docs first
- when a claim depends on external behavior (library APIs, system semantics, game mechanics, etc.), cite the source you verified against, or mark it as unverified

## Planning vs execution
- IMPORTANT: when asked to "plan", "analyze", "deep-dive", or "research", produce documents only; no Edit/Write (except to the plan file) or Bash mutations until approved
- if a request is ambiguous between planning and implementing, ask which one

## Scope
- if a diff grows beyond the original request, stop and confirm before continuing

## Workflow
- when redirected or interrupted, stop the current approach immediately and follow the new direction without explaining or defending it
- focus on one goal per session; don't drift into unrelated improvements
- implement changes directly; don't use sub-agents/Task for simple operations like renames, file moves, or single-file edits
- use Task agents only for genuinely complex parallel exploration or research, not for straightforward implementation

## Comments
- lowercase, no trailing punctuation
- plain: `# descriptive but non-verbose comment`
- keyword: `# KEYWORD:(@janezicmatej) descriptive but non-verbose comment`
- keywords: WARN, FIX, NOTE, TODO, PERF, TEST, HACK
- keyword comments must always include the `(@janezicmatej)` attribution

## Git
- agents MUST commit with `--no-gpg-sign`
- when implementing multi-step work, split into logical commits the user can review and stage independently; don't bundle everything into one
