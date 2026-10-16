# Diagnostics rules

The long form of the headline rules in `CLAUDE.md`.

- Say what the cause is, with the evidence (file and line, log excerpt, command output), before proposing a fix. For system, boot, network and regression bugs, also say which other cause you ruled out and why.
- A workaround is labelled as one, with what would have to change to make it unnecessary. Don't mask an error with a try/except, a retry or a flag without asking first.
- If the fix doesn't resolve the symptom, go back to the cause; don't stack another patch on top.
- Done means the reported behaviour is now right, checked by re-running what failed. An error that went away is not enough. If the fix touched a process, daemon or background job, check it left nothing behind (processes, sockets, locks, temp files).
