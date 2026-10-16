# Notes rules

Each project keeps its local working notes in `.notes/` at the project root: design docs, work that spans sessions, and questions parked for later. The notes are never committed to the project. The `notes` skill does the mechanics (creating the dir, picking ids, close-out).

## Layout

```
.notes/            # its own git repo, never pushed
  README.md        # one line pointing here
  index.html       # generated: the overview, links only
  notes.css        # generated: copy of the skill's stylesheet every page uses
  _pages/          # generated: questions, briefs and other markdown rendered to pages
  _out/            # generated: other/out/ made self-contained, css inlined, for sending
  docs/            # dNNN-slug.html, or dNNN-slug/index.html with its assets
  work/            # wNNN-slug/ while in flight, removed at close-out
  questions/       # qNNN-slug.md, removed when settled
  other/
    in/            # placed by the user
    out/           # prepared for someone else
```

- created on first need (the first doc, work item or question in a project), not up front
- the generated files are rebuilt by the skill's `notes.py` on every commit and never committed; browse every project's notes at once with `notes.py serve` (one port, roots `$NOTES_ROOTS`, else `~/git`), or one project with `python -m http.server -d .notes`
- every page has a back link to the index; ids like `d007` or `q014` in markdown become links

## Numbering

- `<letter><NNN>-<slug>`: `d` docs, `w` work, `q` questions; each letter has its own counter, three digits, lowercase kebab slug
- numbers are never reused, including numbers of deleted items: the next id is the highest ever used in that bucket (files plus `git -C .notes log --all --name-only`) + 1
- refer to items by id everywhere: chat, other notes, commit subjects ("see q014", "per d007")
- `other/` is not numbered

## docs

- point-in-time design docs: plans, proposals, research, reviews; html per the output format rules
- one look for all docs: link `notes.css`, start `main.page` with `nav.back`, use only the components documented at the top of `notes.css`, no `<style>` or font links of their own; the skill shows the skeleton
- a doc with assets becomes a folder: `dNNN-slug/index.html` plus its files, linked relatively
- a status line sits directly under the title as `<p class="status current|stale|superseded">…</p>` (`notes.py` reads it): `status: current`, `status: partly stale (<what changed>, <date>)` or `status: superseded by dNNN (<date>)`, with `dNNN` a relative link to the newer doc
- once done, a doc's body doesn't change; only its status line does. a new design gets a new doc

## work

- one folder per piece of work that spans sessions; a single-session task gets none
- typical files: `brief.md` (goal, done when, scope, decisions to ask), `plan.html` (the proposal to approve), `report.md` (what was built, what differs, leftovers), plus research the work needed
- close-out runs in the same session the work ends (branch merged or work dropped):
  1. lasting design goes to `docs/`: a new doc, or a status line on an existing one
  2. leftovers go to `questions/`, one each, with `origin: wNNN`
  3. delete the folder and commit
- a folder untouched for weeks with no open branch gets flagged to the user, not closed silently

## questions

- one file per item: something deferred, handed off or out of scope for the current session
- frontmatter: `created` (date), `origin` (`wNNN`, `dNNN`, a branch, or `<commit>:<path>` in `.notes`), `status: open`
- body: what is open, why it matters, what is known, where to look
- before acting on one, check the repo for whether it still applies
- settled: fold the outcome into a doc or a work item if it is worth keeping, delete the file, commit with a subject saying how it was settled

## other

- `in/`: read only when the user points at it
- `out/`: written for a person, not for later sessions; don't treat it as context
- html in `out/` uses the same `notes.css` and components as docs, without an id or status line; the copy that leaves is the generated self-contained one in `_out/`
- `out/` holds documents and the few small files that go with them (a script, a config snippet); bulk output for a person (screenshot sets, builds, logs) does not go into `.notes/` at all: in a sandbox vm it goes to the host handoff mount once there is one, until then ask where

## History

- `.notes/` is its own git repo with no remote, its `.gitignore` holding the generated files; commit after each change set, subject line only, naming the ids touched (`q014: settled by a3f4573`)
- git history replaces archives: delete instead of moving to an archive folder, rewrite instead of keeping dated copies
- never stage `.notes/` from the project repo: stage project paths explicitly, never `git add .` or `git add -A` there
- the host's global gitignore hides `.notes/`; where it shows up as untracked (sandbox vms), that is expected

## What doesn't go in notes

- facts every session needs: the project's `AGENTS.md`/`CLAUDE.md`, or memory when they are personal
- anything teammates need: the project repo
- secrets
- committed project files never reference `.notes/` paths
