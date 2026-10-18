# Notes

Each project keeps its local working notes in `.notes/` at the project root, its own git repo with no remote, never pushed and never committed to the project. Every step that changes it ends with `commit`, which also regenerates the generated files (never committed): `index.html`, `notes.css`, `_pages/` (markdown rendered), `_out/` (`other/out/` made self-contained). Change the look only in `notes.css` next to this file.

Who reads what: Matej reads the work item, starting at its brief's `## Your move`, the pages it links, and his questions; nothing else. Docs, follow-ups and the rest of a work folder are the lead's and the agents', shaped for them. The index lists only work items and questions; everything else is still rendered, so a link from a work item opens.

```
N=~/.config/claude/skills/lead/notes.py
python3 $N init                 # create .notes/ if missing (idempotent)
python3 $N next d|w|f|q         # next free id, counts deleted items too
python3 $N new d <slug>         # docs/dNNN-slug.md on the skeleton; --html for a doc with a diagram
python3 $N new w <slug>         # work/wNNN-slug/brief.md on the skeleton
python3 $N commit "<subject>"   # regenerate, then commit all of .notes/
python3 $N index                # regenerate only
python3 $N status               # open work items: move, next, decisions waiting, branches in main or not; counts
python3 $N file wNNN <part> <output-file|agent-id> --checked "<what the lead checked>"
                                # the agent's final reply, verbatim, into work/wNNN-*/report-<part>.md
python3 $N serve                # every project's notes on http://127.0.0.1:8765/, decide clicks recorded (the user runs this)
```

All commands take `--root <project>`; the default is the git toplevel of the current dir. Never pick an id by hand: ids are `<letter><NNN>-<slug>` (`d` docs, `w` work, `f` follow-ups, `q` questions, three digits, kebab slug), never reused, and deleted ones live only in git history. Refer to items by id everywhere ("see q014", "per d007"); in markdown an id becomes a link.

```
.notes/
  docs/       dNNN-slug.md, or .html / dNNN-slug/index.html for a doc with a diagram and its assets
  work/       wNNN-slug/ while in flight, removed at close-out
  followups/  fNNN-slug.md, removed when done or moot
  questions/  qNNN-slug.md, Matej's own, removed when he settles them
  other/in/   placed by the user, read only when pointed at
  other/out/  prepared for someone else
```

Markdown for everything, docs included: they are agent-facing. HTML only for a diagram Matej needs, linked from his work item. Screenshot a page (headless browser, light and dark) only when it has a diagram or a decide block.

## Docs

Point-in-time records of a type: `plan` (a proposal to approve), `research` (findings with sources), `review` (what a review found and what was done), `as built` (the lasting design of finished work, written at close-out).

- `new d <slug>`, then fill it in. The markdown skeleton's frontmatter holds `type`, `date` and `status`; the html one (`--html`) links `notes.css`, starts `main.page` with `nav.back`, and uses only the components listed at the top of `notes.css`, no `<style>` or font links. A folder doc's relative paths gain one `../`.
- status: `current`, `partly stale (<what changed>, <date>)` or `superseded by dNNN (<date>)`; in html, `<p class="status current|stale|superseded">status: …</p>` under the title, with `dNNN` a relative link. Replacing a doc means setting the older one's status.
- Once done, only a doc's status changes; a new design gets a new doc.
- At close-out a plan or review doc is deleted once its lasting decisions are in an as-built doc or in the code. "Partly stale" doesn't outlive the next session: fix the doc or delete it.
- `commit "dNNN: <slug>"`

## Work items

One folder per piece of work that spans sessions; a single-session task gets none. It is the handoff: a later session picks the work up from the folder alone.

- `new w <slug>` writes `brief.md`: goal, `## Your move`, done when, scope, prerequisites, and `## Decided` with each locked decision and its date.
- `## Your move` is Matej's entry point: one to three lines with links (a page to read, a decision to click). The page opens with it in a box, with links to the decisions still waiting and the item's branches, in main or not. The lead keeps it current and its chat reply points at the page instead of asking in chat.
- The brief holds the current state, not its history: a replaced decision, fact or next step is edited in place, and git keeps the old one. An agent's brief cites brief sections and at most one report section, never whole reports or folders.
- As the work goes: `plan.md` (the proposal), a brief per phase or part an agent builds, `report-<part>.md` per reply, `made.md` (every branch, worktree, container and folder the work created, with its state; whether a branch is in main, `status` reads from git), research, and `decisions.md` (written by `serve`; the lead copies its entries into `Decided` and leaves them there, and appends a choice Matej gives in chat as `- <date> <key>: <choice> (matej, in chat)`, so the block shows it chosen and `status` stops listing it).
- Replies are filed with `file` when the notification arrives, from its `<output-file>` or the agent id: the lead types only the check line, never the reply. Its transcript's last reply changes if the agent goes on later, so file each reply on its notification.
- `commit "wNNN: <what changed>"`. A folder untouched for weeks with no open branch: tell the user, don't close it.

### Decisions in a page

A fenced block in any markdown file of a work item:

````
```decide d1-policy
a*) fold into the skill
one file, loaded only with the skill
b) a path-scoped rule
keeps two files
```
````

The info string is `decide <key>` (`[a-z0-9-]`); an option starts with `<letter>) <title>`, `*` before the `)` marks the recommended one, and the lines up to the next option are its text. It renders as two options side by side, each with a button. Under `serve` a click appends `- <date> <key>: <choice> (matej, clicked)` to the item's `decisions.md`, commits `wNNN: <key> decided, <choice>`, and the page marks the chosen option; `git -C .notes log -1` shows it when Matej says he decided. Opened without `serve`, the block shows a line for him to paste instead (`w012 d1-policy: a|b`). `serve` accepts only loopback, same-origin posts, and only an option the item's own pages offer for that key.

## Close-out

When the work's branch is merged or the work is dropped, in that same session:

1. lasting design: a new `as built` or `review` doc, or a status line on an existing one; delete the plan and review docs it covers (see Docs)
2. leftovers: follow-ups (below), by area; never questions
3. remove everything `made.md` lists, `rm -r work/wNNN-slug`, `commit "wNNN: closed, <merged as <sha>|dropped>; <dNNN, fNNN touched>"`

## Follow-ups

What finished work found and left undone (defects, rough edges, unverified claims, ideas, to-dos after a deploy), one file per area, not per item.

1. a file for the area exists: append `## From wNNN, <date>` and add `wNNN` to its `origin`
2. otherwise `next f` and write `followups/fNNN-slug.md`: frontmatter `created`, `origin: wNNN`, `status: open`; `# <the area, as a noun phrase>`; then per item what it is, the evidence (`file:line`, a commit, a measurement) and a direction in a line, so a session with no memory of today can act on it
3. `commit "fNNN: <what was added>"`

Settling: check the repo first (items go stale), remove the done or moot items, `rm` an empty file, `commit "fNNN: <items> settled, <done in <sha> | moot because ...>"`. A follow-up area becomes work by a work item that cites it.

## Questions

Matej's own. Park one only when he asks, in his words; never for your own leftovers.

1. `next q`, write `questions/qNNN-slug.md`: frontmatter `created`, `asked-by: matej`, `origin`, `status: open`; `# <his question>`; `## Known` with what is known, sourced, and where to look (you may add sourced facts there later, never new questions)
2. `commit "qNNN: <slug>"`

Settling: check the repo first, fold the outcome into a doc or work item if worth keeping, `rm` the file, `commit "qNNN: settled, <done in <sha> | moot because ... | moved to wNNN>"`.

## Other

`other/out/` holds documents for someone else, written for that reader, and the few small files that go with them; no ids, no status line. HTML there follows the doc skeleton with `../../notes.css`; the eyebrow names the reader and date (`for the team · 2026-10-14`). What gets sent is the generated `_out/<file>`; look at it before handing it over, link it from the work item's `## Your move` (the index doesn't list `other/`), then `commit "other: <file>"`. Bulk output for a person (screenshots, builds, logs) goes to the host handoff mount, not `.notes/`.

## Never

- stage `.notes/` from the project repo (`git add .`, `git add -A`), or reference `.notes/` paths from committed project files
- keep archives or dated copies: delete, git keeps it
- push `.notes/` or add a remote
- put in notes what every session needs (AGENTS.md, CLAUDE.md, memory), what teammates need (the project repo), or secrets
