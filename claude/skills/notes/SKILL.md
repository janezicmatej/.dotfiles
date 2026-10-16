---
name: notes
description: Manage the project's local .notes/ dir (design docs, work handoffs, parked questions). Use whenever writing a design doc, plan, proposal, research or review for local use; starting, handing off or closing out work that spans sessions (brief, plan, report); parking something for later, out of scope or a follow-up; picking up or settling a parked question; preparing a document for someone else; or when the user mentions .notes, handoffs, open questions or asks what is pending.
---

# Notes

The policy is `~/.config/claude/rules/notes.md`: layout, numbering, status lines, close-out, what doesn't belong. This skill holds the procedures. Every step that changes `.notes/` ends with `commit`, which also regenerates `index.html`, `notes.css`, the markdown pages under `_pages/` and the portable copies under `_out/`. Change the look only in this skill's `notes.css`, never in a project.

```
N=~/.config/claude/skills/notes/notes.py
python3 $N init                 # create .notes/ if missing (idempotent)
python3 $N next d|w|q           # next free id, counts deleted items too
python3 $N commit "<subject>"   # regenerate the generated pages, commit all of .notes/
python3 $N index                # regenerate index.html, notes.css, _pages/ and _out/ only
python3 $N serve                # every project's notes on http://127.0.0.1:8765/: hub filters projects, each project page searches its notes (the user runs this)
```

All commands take `--root <project>`; the default is the git toplevel of the current dir. Never pick an id by hand or from `ls`; deleted ids live only in git history.

## New doc

1. `init`, then `next d`
2. write `docs/dNNN-slug.html` (or `docs/dNNN-slug/index.html` with its assets next to it, then every `../` below becomes `../../`) on this skeleton, using only the components documented at the top of `notes.css` (callout, tag, cards, grid-2, table, figure.diagram with its svg classes); no `<style>`, no font links:

   ```html
   <!doctype html>
   <html lang="en">
   <head>
   <meta charset="utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <title>Short name</title>
   <link rel="stylesheet" href="../notes.css">
   </head>
   <body>
   <main class="page">
   <nav class="back"><a href="../index.html">← notes</a></nav>
   <header>
     <p class="eyebrow">dNNN · plan · 2026-10-14</p>
     <h1>Title</h1>
     <p class="status current">status: current</p>
     <p class="lede">What this doc decides, in one or two sentences.</p>
   </header>
   <section>
     <h2>…</h2>
   </section>
   </main>
   </body>
   </html>
   ```

3. if it replaces an older doc, set the older one's status line to `<p class="status superseded">status: superseded by <a href="dNNN-slug.html">dNNN</a> (<date>)</p>`; mind the relative path when either doc is a folder
4. look at it: a headless browser screenshot in light and dark, or `serve`
5. `commit "dNNN: <slug>"`

## New work item

Only for work that will span sessions.

1. `init`, then `next w`, create `work/wNNN-slug/`
2. `brief.md`, starting with `# wNNN <title>`: goal, done when, scope, verification, decisions to ask, prerequisites to read
3. add `plan.html` (the proposal, on the doc skeleton with `../../notes.css` and `../../index.html`) and research files as the work goes; `report.md` at the end: what was built, what differs from the plan, leftovers
4. `commit "wNNN: <what changed>"`

## Close-out

When the work's branch is merged or the work is dropped, in that same session:

1. lasting design → new doc or a status line on an existing one (see above)
2. each leftover → a question with `origin: wNNN`
3. `rm -r work/wNNN-slug`, then `commit "wNNN: closed, <merged as <sha>|dropped>"`

When `index` shows a work folder untouched for weeks with no open branch in the project, tell the user; don't close it yourself.

## Park a question

1. `init`, then `next q`
2. write `questions/qNNN-slug.md`:

   ```
   ---
   created: 2026-10-14
   origin: w009
   status: open
   ---

   # <one-line question or follow-up>

   What is open and why it matters. What is known so far, with paths, commits and ids.
   Where to start looking.
   ```

3. `commit "qNNN: <slug>"`

Write it so a session with no memory of today can act on it.

## Settle a question

1. check the repo first: it may already be done or moot
2. fold the outcome into a doc or a work item if it is worth keeping
3. `rm questions/qNNN-slug.md`, `commit "qNNN: settled, <how: done in <sha> | moot because ... | moved to wNNN>"`

## Other

- `other/in/`: the user's files; read only when pointed at
- `other/out/`: documents for someone else, written for that reader; no ids, no status line
  - html follows the doc skeleton and components like any doc, with `../../notes.css` and `../../index.html`; the eyebrow names the reader and date instead of an id (`for the team · 2026-10-14`)
  - what gets sent is the generated `_out/<file>`: `notes.css` inlined, back link dropped, other files copied; the index links it as "to send"
  - look at the `_out/` copy too before handing it over, then `commit "other: <file>"`

## Never

- stage `.notes/` from the project repo (`git add .`, `git add -A`); stage project paths explicitly
- reference `.notes/` paths from committed project files
- keep archives or dated copies; delete, git keeps it
- push `.notes/` or add a remote
