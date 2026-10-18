---
name: ground-rules
description: Ground rules shared by every agent type, preloaded by them; not for direct use.
user-invocable: false
---

# Ground rules

- no `bash -c` or `sh -c` wrappers, also not inside `docker exec` or `docker run`: write the script to a file, run `bash <file>`
- remove by literal path or `"${DIR:?}"/name`; never `$DIR/*`, never the cwd or its parents; worktrees with `git worktree remove`
- never `git stash`: use `git show <rev>:<path>` or a scratch copy
- run project tools (uv, ruff, pnpm) only from your worktree, never the main checkout; tool state (venvs, caches, `node_modules`: `UV_PROJECT_ENVIRONMENT`, `RUFF_CACHE_DIR` and the like) under `$SANDBOX_VM_STATE`, never in a host mount
- if the harness refuses something, stop and report it; never work around it
- find with grep, read line ranges, not whole files; send long output (builds, docker, tests) to a log file and show its tail and the failures
- wait on a long job with Monitor in the same turn; never reply with a job still running
