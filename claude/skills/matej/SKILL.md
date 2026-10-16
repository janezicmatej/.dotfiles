---
name: matej
description: How Matej likes larger work run - one lead session that talks to him and briefs agents, a senior agent that builds and hands back a checked branch, explorer agents for open questions, notes and a design canvas for review. Use when he asks for orchestrated work ("let the senior handle it", "spawn agents for this", parallel options to compare) or for work spanning several branches or sessions.
---

# Running work through agents

Guidelines, not a procedure. Where a step is obvious, do it your way; what is written here is what isn't knowable from the repo.

## Roles

- **Lead**: the session Matej talks to. Discusses, locks decisions, keeps the notes, briefs agents, checks what they report and tells him plainly what is done, what is open and what it took on trust. It doesn't edit the project itself, so its context stays free for judgement.
- **Senior**: owns a unit of work from brief to a branch that works, and hands back that one branch, never merging it.
  - When the work splits into parts that don't step on each other, it runs implementer agents in parallel, each on its own branch and worktree under the work id, briefed the way the lead briefs it. A few at a time; what everything else builds on (a shared shell, a schema) goes first, alone. Small or tightly coupled work it does itself.
  - It reviews each part before taking it in (reads the diff, runs code-review and simplify, fixes what is real), condenses its history, and merges it into the work's integration branch, sorting out what parallel parts collide on (migrations, generated code).
  - It runs every check the project has on the integration branch, not only on the parts, and looks at what changed in a browser when there is UI.
  - It removes its implementers' branches, worktrees and containers once they are merged, and its own when it hands back; the lead checks.
- **Explorers**: answer an open question with something Matej can inspect, often two independently on the same brief so he can compare. Prototypes may cut corners; they never land as they are.

## Protocol

- Discuss, lock, relay. Only locked decisions go to builders, in the words that were agreed. When a relay replaces an earlier one, say what it replaces; when unsure what Matej meant, ask before relaying.
- Builders keep going while the next point is discussed; new locked items join the open branch.
- Builders decide what the brief doesn't settle the simple way and list it as "decided along the way". Only the lead asks Matej.

## Spawning

Use the agent types for the roles (`senior`, `junior`, `explorer`, `researcher` in `~/.config/claude/agents/`), not a general-purpose agent, so Matej sees who is doing what. An agent's label is set once, when it is spawned, so make it the top level: the unit of work it is for ("graph redesign", "how it works redraw", "signing agent commits"), never its first step. What it is doing right now is the activity Claude Code shows beside the label; that part takes care of itself. When a running agent is given a new item, the label stays as it was, so say the new item in the relay's first line.

## A brief carries

The goal and what done looks like; where the spec is (note ids, canvas frames, branches); the decisions that touch it; scope and what not to touch; pointers to the rules (AGENTS.md, CLAUDE.md, the house skills) rather than copies; the checks; the shape of the reply; what it may create and must clean up. Agents don't see the lead's memory: anything they need from it goes in the brief.

## Before passing a report on

Check the cheap facts yourself: branch heads, commit authors and subject lengths, nothing staged that shouldn't be, worktrees and containers gone. Re-run something long only when a claim looks off. Say what you checked.

## Where things go

- Plans, decisions, reports, leftovers: the project's `.notes/` (the notes skill). Agents can't write there; the lead files their reports.
- Visual design to discuss: the Design canvas (an Artifact), kept current; history frames get removed, not piled up.
- Prototypes and finished work: branches. The repo's `.git` is on Matej's host, so he can `git worktree add --detach` any branch there.
- Bulk files for Matej (screenshots, logs): the host handoff mount once it exists; never the project repo, never bulk in `.notes/`.

## Ownership and clean-up

- Everything a unit of work creates carries its work id: branches `<wNNN>/<name>`, worktrees under `$SANDBOX_VM_STATE/wt/<wNNN>/`, containers `<wNNN>-<name>`. Agents remove what they created and nothing else.
- The lead keeps `made.md` in the work item: each branch, worktree, container and handoff folder, with its state (open, merged, prototype).
- Close-out removes the list: merged branches deleted, prototypes once their decision is recorded, worktrees, containers and handoff folders gone; then check nothing under the work id is left.

## Interruptions

Any agent can stop (usage limits, Matej stopping it), and a stopped agent can't be resumed. Keep state on disk: small commits on the branch, decisions and reports in the work item. Before re-briefing, look at the repo first and hand the new agent what is actually there.

## Git

Agents never sign; Matej re-signs on his host before pushing (CLAUDE.md, Git).
