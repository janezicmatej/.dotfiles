# Global CLAUDE.md

## Output format
- for plans, reports, design docs, and anything benefiting from diagrams, styling, or embedded images, prefer HTML over Markdown
- for conventional files (README, CONTRIBUTING, LICENSE, CHANGELOG, etc.) use the ecosystem default

## Notes
- local design docs, work handoffs and parked questions live in `.notes/` per project (see ~/.config/claude/rules/notes.md)

## Diagnostics
- IMPORTANT: find the root cause before proposing a fix; never present a workaround as a fix (see ~/.config/claude/rules/diagnostics.md)
- if a fix doesn't resolve the symptom, revisit the cause instead of layering patches

## Trust & verification
- IMPORTANT: don't present plausible-sounding details as facts; verify file paths, flags, function and library behavior by reading code or docs first
- when a claim depends on external behavior (library APIs, system semantics, game mechanics, etc.), cite the source you verified against, or mark it as unverified

## Planning vs execution
- IMPORTANT: when asked to "plan", "analyze", "deep-dive", or "research", produce documents only; no Edit/Write (except to the plan file or `.notes/`) or Bash mutations until approved
- if a request is ambiguous between planning and implementing, ask which one

## Scope
- don't start unrelated work on your own; if a diff grows beyond the request, stop and confirm
- in orchestrated work (the `matej` skill), an agent working from a brief stays inside the brief instead: it notes anything outside it as a leftover and keeps going

## Comments
- lowercase, no trailing punctuation
- plain: `# descriptive but non-verbose comment`
- keyword: `# KEYWORD:(@janezicmatej) descriptive but non-verbose comment`
- keywords: WARN, FIX, NOTE, TODO, PERF, TEST, HACK
- keyword comments must always include the `(@janezicmatej)` attribution

## Git
- agents never sign commits, in any form: they are not me. commit with `--no-gpg-sign`; I re-sign branches on my host (`git sign-branch`) before they are pushed
- use the identity git already has; where it has none, commit as `-c user.name=agent -c user.email=agent@sandbox.invalid` (my host signing resets the author)
- commit messages: a conventional-commit subject line of at most 72 characters including the prefix; a body only where the project wants one, wrapped at 72; no trailers
- stage paths explicitly; never `git add .` or `git add -A`
- split multi-step work into a few logical commits I can review; condense fixups before handing a branch back
- every branch, worktree and container you create is yours to remove when the work ends; never remove ones you did not create
