# Diagnostics rules

Detailed root-cause discipline for system, boot, network, and regression bugs. The headline rules live in `CLAUDE.md`; this file is the long form.

## Root-cause hypothesis

Before proposing any fix for a system/boot/network/regression bug, write a "Root cause hypothesis" section with these four parts:

1. **Symptom** — the observable behavior, copied verbatim where possible (error message, missing output, wrong value)
2. **Proximate cause** — the immediate trigger, with evidence (file path + line, log excerpt, command output)
3. **Underlying cause** — why the proximate cause occurred; the layer of indirection that makes the proximate cause possible
4. **Ruled-out alternative** — at least one other plausible hypothesis you considered and why you discarded it

Only after writing all four parts should you propose a fix.

## Workaround discipline

- never present a manual workaround as a fix; if a workaround is the only option, label it explicitly as a workaround and describe what would need to change to make it unnecessary
- if a fix doesn't resolve the symptom on first try, don't layer another patch; revisit the hypothesis instead
- if you're tempted to add a try/except, retry loop, or feature flag to mask an error, stop and ask first

## Verification

- before declaring a fix done, re-run the failing check and confirm the reported behavior is now correct
- "the error message disappeared" is not sufficient; confirm the underlying behavior matches what was expected
- if the fix touches a process, daemon, or background job, confirm it cleaned up after itself (no orphaned procs, sockets, locks, temp files)
