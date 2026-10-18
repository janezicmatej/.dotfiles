---
name: lead
description: How Matej likes larger work run and its notes kept - a lead session that talks to him and briefs agents, an integrator that hands back a checked branch, builders, researchers and explorers, and the project's local .notes/ (docs, plans, work handoffs, follow-ups, his parked questions). Use when he asks for orchestrated work ("let the integrator handle it", "spawn agents for this", options to compare), for work spanning several branches or sessions, or whenever writing, handing off, closing out or settling anything in .notes/, or when he asks what is pending.
---

# Running work through agents

Guidelines, not a procedure. What is written here is what isn't knowable from the repo.

## Roles

- **Lead**: the session Matej talks to. Discusses, locks decisions, keeps the notes, briefs agents, checks their replies. It doesn't edit the project, so its context stays free for judgement. One work item per lead session: at a natural break it hands off through the work folder and Matej starts a new session, which starts with `notes.py status`. Its replies state outcomes and decisions and what it took on trust, and point Matej at the work item's page, whose `## Your move` says what he does next; detail stays in the notes.
- **Integrator** (`integrator`): owns a unit of work (a phase, or the whole item when it has one part) from brief to one branch that works. It merges its builders' parts into its own branch, never its branch into the work branch or `main` (see Git).
  - Parts that don't step on each other go to builders in parallel, at most 2–3 at a time, each on its own branch and worktree under the work id. What everything else builds on (a shared shell, a schema) goes first, alone. Small or tightly coupled work it does itself.
  - It reads each part's diff, fixes what is real or sends it to a fresh builder, condenses the part's history, and merges it with `--no-ff`, sorting out what parallel parts collide on (migrations, generated code).
  - On the integrated branch, once: code-review and simplify, every check the project has (see Tests), and a browser look when there is UI.
  - It removes its builders' branches, worktrees and containers once merged, and its own when it hands back.
- **Builders** (`builder-sonnet`, `builder-opus`): one part each, from the integrator's brief.
- **Researchers** (`researcher-sonnet`, `researcher-opus`): a verified answer with sources.
- **Explorers** (`explorer`): an option Matej can inspect. Prototypes may cut corners; they never land as they are. A prototype branch ends in `-prototype` (`wNNN/<name>-prototype`), so `notes.py status` doesn't count it as work to merge.

## How many agents

One agent per question. Two independent ones only for security and quality reviews, and for a decision Matej flags as core. Any agent that runs others runs at most 2–3. A sharp brief to one researcher beats a manager with a team.

## Models

The pair types carry their model in their frontmatter; never pass a `model` when spawning them, it overrides the frontmatter. The lead picks researchers, the integrator picks builders, by the type descriptions: Sonnet for fully specified, few files, an existing pattern, fast checks (builders) or a clear answer in known sources with a short scripted check (researchers); Opus for debugging, VMs or containers, security, open design, shared code, measurements, comparisons, core decisions, or when unsure. A Sonnet agent that fails its checks twice, gets stuck or comes back thin is replaced by a new Opus agent, briefed from its branch or reply. Integrator and explorer run on the default model.

## Protocol

- Discuss, lock, relay. Only locked decisions go to agents, in the words agreed. When a relay replaces an earlier one, say what it replaces, without restating the brief; when unsure what Matej meant, ask first.
- Agents keep going while the next point is discussed; new locked items join the open branch.
- Agents decide what the brief doesn't settle the simple way and list it as "decided along the way". Only the lead asks Matej.
- Once an agent has replied, it is done. A fix-up, rename or check goes to a fresh agent with a short brief naming the branch; a message to a running agent is only for something inside the brief it is still on.

## Spawning

Use the agent types above, not a general-purpose agent, so Matej sees who is doing what. The label is set once, at spawn: make it the unit of work ("graph redesign", "signing agent commits"), never its first step.

## A brief carries

The goal and what done looks like; where the spec is, as note ids and sections: brief sections and at most one report section, never whole reports, folders or "everything it points to"; the decisions that touch it; scope and what not to touch; the checks with the test scope for the role; the reply shape when it differs from the agent's; what it may create and must clean up. Agents don't see the lead's memory: what they need from it goes in the brief. The standing rules (shell wrappers, `rm` paths, stash, tool state, refusals, quiet output, waiting on jobs, reply shape) are in the ground-rules skill, preloaded by every agent type; briefs don't restate them.

## Tests: who runs what

- **While building a part**: only the tests for what was touched (new tests, the changed modules' test files, tests that import them), plus lint and format on the changed files. Name the selection in the reply.
- **Before a part is merged**: the integrator runs the whole suite of each project member the part touched; live or slow tests (VMs, external services, browsers) only when the part touches what they cover.
- **Once, before reporting**: the integrator runs every check the project lists, on the integrated branch, as CI does. The reply's numbers come from this run.
- **The lead never re-runs suites.** It checks the cheap facts, and re-runs something only when a claim looks off.

## Before passing a reply on

Check the cheap facts: branch heads, commit authors and subject lengths, nothing staged that shouldn't be, worktrees and containers gone. Say what you checked.

## Tuning this flow

A change to this skill, the agent definitions or the notes conventions is kept with its measured difference: replay a finished task on its frozen commit with the old and the new files and compare tokens and outcome from the transcripts. Each kept change gets a line in the work item's as-built doc.

## Where things go

- Plans, decisions, replies: the work item in `.notes/` (see Notes). Its brief holds the current state: a replaced decision is edited in place, git keeps the old one. Agents can't write there; the lead files each reply with `notes.py file` when the notification arrives, and never retypes it.
- Leftovers: `followups/`, by area, at close-out. `questions/` is Matej's own.
- Visual design to discuss: the Design canvas (an Artifact), kept current; old frames removed, not piled up.
- Prototypes and finished work: branches. The repo's `.git` is on Matej's host, so he can `git worktree add --detach` any branch.
- Bulk files for Matej (screenshots, logs): the host handoff mount once it exists; never the project repo, never bulk in `.notes/`.

## Notes

Plans, decisions, work handoffs, follow-ups and Matej's questions live in the project's `.notes/`. Before writing, closing out or settling anything there, read `notes.md` next to this file: layout, ids, the `notes.py` commands (`~/.config/claude/skills/lead/notes.py`), decide blocks, close-out.

## Ownership and clean-up

- Everything a unit of work creates carries its work id: branches `<wNNN>/<name>` (see Git), worktrees under `$SANDBOX_VM_STATE/wt/<wNNN>/`, containers `<wNNN>-<name>`. Agents remove what they created and nothing else.
- The lead keeps `made.md` in the work item: each branch, worktree, container and handoff folder, with its state (open, merged, prototype); whether a branch is in main, `notes.py status` reads from git.
- Close-out removes the list, then checks nothing under the work id is left.

## Interruptions

Any agent can stop (usage limits, Matej stopping it) and can't be resumed. Keep state on disk: small commits, decisions and replies in the work item. Before re-briefing, look at the repo and hand the new agent what is actually there.

## Git

Agents never sign; Matej re-signs on his host before pushing (CLAUDE.md, Git).

```
main
└─ wNNN/<work>          the work branch, off main; Matej merges it into main
   ├─ wNNN/phase1       an integrator's branch, off wNNN/<work>
   │  ├─ wNNN/phase1-api    a builder's part, off wNNN/phase1
   │  └─ wNNN/phase1-ui
   └─ wNNN/phase2       off wNNN/<work> once phase1 is merged into it
```

- Each level branches from the one above and goes back with a merge commit (`merge: <what>`, unsigned), so every phase and part stays one merge in the history.
- `<work>` is a short kebab name, usually the item's slug. Never plain `wNNN`, and phases and parts are siblings under `wNNN/`, never under `wNNN/<work>/`: git can't hold a branch next to branches below it. The lead creates the work branch off `main` when the first phase is briefed.
- One part, no phases: the integrator's branch is `wNNN/<work>` itself.
- Parts: the integrator merges each into its phase branch with `git merge --no-ff`.
- Phases: once the lead has checked a phase's reply, it merges the phase branch into `wNNN/<work>` with `--no-ff` and deletes it, right away; the next phase branches off that merge commit, never off the previous phase's tip. A conflict goes to an integrator; the lead doesn't resolve code.
- A phase that must start before the previous one is merged branches off its tip, then is rebased onto the merge commit (`git rebase --onto <merge> <previous tip>`) before it is merged.
- A work item built on another one not yet in `main` starts from that one's work branch tip; once Matej merges it (his signing rewrites the shas), the lead rebases with `--rebase-merges` onto that merge commit.
- Two branches that conflict (a refactor and a fix pass on the same code) aren't resolved hunk by hunk. An integrator, for each conflicting part, picks the better implementation (more correct, tested, fits the code) and says why; adopts it; rebuilds the other branch's remaining intent as new commits on a fresh branch off the winner; runs every check; and lists what was adopted, rebuilt and dropped. The lead only picks which pairs need it.
- Only Matej merges into `main`.
