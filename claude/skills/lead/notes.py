#!/usr/bin/env python3
"""mechanics for a project's .notes/ dir, see notes.md next to it

usage:
  notes.py [--root DIR] init              create .notes/ with its git repo, if missing
  notes.py [--root DIR] next d|w|f|q      print the next free id of a bucket
  notes.py [--root DIR] new d|w SLUG [--html]
                                          write a doc (markdown, or html with --html) or a work
                                          item's brief.md on its skeleton, with the next free id
  notes.py [--root DIR] index             regenerate index.html, notes.css, the markdown pages and
                                          the portable copies of other/out/ in _out/
  notes.py [--root DIR] commit SUBJECT    regenerate the index, commit every change in .notes/
  notes.py [--root DIR] status            open work items: the move, next, decisions waiting,
                                          their branches in the project's git; follow-up counts
  notes.py [--root DIR] file WORK PART TRANSCRIPT --checked TEXT
                                          an agent's final reply, verbatim from its transcript (the
                                          notification's output-file or the agent id), into
                                          work/WORK-*/report-PART.md under the lead's check line
  notes.py serve [--port 8765] [--roots DIR ...]
                                          every project's notes on one port; roots default to
                                          $NOTES_ROOTS, else ~/git; a click in a decide block
                                          appends to the work item's decisions.md and commits

DIR is the project root, by default the git toplevel of the current dir, else the current dir
"""

import argparse
import html
import json
import os
import posixpath
import re
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

BUCKETS = {"d": "docs", "w": "work", "f": "followups", "q": "questions"}
ID_RE = re.compile(r"^(docs|work|followups|questions)/([dwfq])(\d{3})-")
README = "Local notes, never pushed. Layout and rules: ~/.config/claude/skills/lead/notes.md\n"
# a page's tab icon: a rounded square in the orange accent
ICON = (
    '<link rel="icon" href="data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
    "%3Crect width='16' height='16' rx='4' fill='%23c35e0a'/%3E%3C/svg%3E\">"
)


def git(notes: Path, *args: str, check: bool = True) -> str:
    return subprocess.run(
        ["git", "-C", str(notes), *args], check=check, capture_output=True, text=True
    ).stdout


def project_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    root = Path(out.stdout.strip()) if out.returncode == 0 else Path.cwd()
    # inside .notes the toplevel is the notes repo itself
    return root.parent if root.name == ".notes" else root


def init(notes: Path) -> None:
    for d in ("docs", "work", "followups", "questions", "other/in", "other/out"):
        (notes / d).mkdir(parents=True, exist_ok=True)
    if not (notes / "README.md").exists():
        (notes / "README.md").write_text(README)
    if not (notes / ".gitignore").exists():
        (notes / ".gitignore").write_text("/index.html\n")
    if not (notes / ".git").exists():
        git(notes, "init", "-q", "-b", "main")
        # NOTE:(@janezicmatej) local-only repo, any identity works when none is configured
        if not git(notes, "config", "user.email", check=False).strip():
            git(notes, "config", "user.name", "notes")
            git(notes, "config", "user.email", "notes@localhost")
        commit(notes, "init notes")
    else:
        write_index(notes)
    print(notes)


def next_id(notes: Path, letter: str) -> str:
    bucket = BUCKETS[letter]
    paths = [f"{bucket}/{p.name}" for p in (notes / bucket).glob("*")]
    if (notes / ".git").exists():
        log = git(notes, "log", "--all", "--name-only", "--pretty=format:", check=False)
        paths += log.splitlines()
    nums = [int(m[3]) for p in paths if (m := ID_RE.match(p)) and m[2] == letter]
    return f"{letter}{max(nums, default=0) + 1:03d}"


def commit(notes: Path, subject: str) -> None:
    write_index(notes)
    git(notes, "add", "-A")
    if git(notes, "status", "--porcelain").strip():
        git(notes, "commit", "-q", "--no-gpg-sign", "-m", subject)
        print(git(notes, "log", "-1", "--oneline").strip())
    else:
        print("nothing to commit")


DOC_MD = """---
type: plan
date: {date}
status: current
---

# {title}

What this doc decides, in one or two sentences.

## …
"""

DOC_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{icon}
<link rel="stylesheet" href="../notes.css">
</head>
<body>
<main class="page">
<nav class="back"><a href="../index.html">← notes</a></nav>
<header>
  <p class="eyebrow">{id} · plan · {date}</p>
  <h1>{title}</h1>
  <p class="status current">status: current</p>
  <p class="lede">What this doc decides, in one or two sentences.</p>
</header>
<section>
  <h2>…</h2>
  <figure class="diagram"><svg viewBox="0 0 640 200" role="img"></svg></figure>
</section>
</main>
</body>
</html>
"""

BRIEF = """# {id} {title}

Goal in a sentence or two.

## Your move

What Matej does next, one to three lines with links (a page to read, a decision to click).

## Done when

## Scope

## Prerequisites

## Decided
"""


def new(notes: Path, letter: str, slug: str, as_html: bool) -> None:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit(f"slug {slug!r} is not lowercase kebab")
    item = next_id(notes, letter)
    fields = {
        "id": item,
        "date": datetime.now().astimezone().date().isoformat(),
        "title": slug.replace("-", " ").capitalize(),
        "icon": ICON,
    }
    if letter == "d":
        path = notes / "docs" / f"{item}-{slug}.{'html' if as_html else 'md'}"
        text = (DOC_HTML if as_html else DOC_MD).format(**fields)
    else:
        path = notes / "work" / f"{item}-{slug}" / "brief.md"
        text = BRIEF.format(**fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(path)


# pages: index.html, notes.css, _pages/ and _out/ are generated, never committed
# each file is written beside itself as .<name>.<random>.partial and renamed over, so a
# reader or a second build never meets half a file or a missing one; no lock or symlink,
# the host and the vms share .notes/ over 9p, which keeps neither

CSS = Path(__file__).with_name("notes.css")
GENERATED = ("/index.html", "/notes.css", "/_pages/", "/_out/", "/.*.partial")
PAGES = "_pages"
OUT = "_out"
PARTIAL = re.compile(r"^\..+\.[0-9a-f]{8}\.partial$")
# a partial file this old is a crashed build's, not one still writing
PARTIAL_AGE = 600
CSS_LINK = re.compile(r'<link\b[^>]*href="[^"]*notes\.css"[^>]*>', re.IGNORECASE)
BACK_NAV = re.compile(r'\s*<nav class="back">.*?</nav>', re.DOTALL | re.IGNORECASE)
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
ID_TOKEN = re.compile(r"(?<![\w/.-])([dwfq]\d{3})(?![\w/-])")


def ensure_gitignore(notes: Path) -> None:
    path = notes / ".gitignore"
    lines = path.read_text().splitlines() if path.exists() else []
    missing = [g for g in GENERATED if g not in lines]
    if missing:
        write_whole(path, "\n".join([*lines, *missing]) + "\n")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m[1].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta, text[m.end() :]


def split_title(body: str, fallback: str) -> tuple[str, str]:
    """first heading as the title, without a leading id, and the body without it"""
    m = re.search(r"^#\s+(.+)\n?", body, re.MULTILINE)
    if not m:
        return fallback, body
    title = re.sub(r"^[dwfq]\d{3}\b\s*", "", m[1].strip())
    return title, body[: m.start()] + body[m.end() :]


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


class Site:
    """what exists in .notes/ and where each item's page is, relative to .notes/"""

    def __init__(self, notes: Path) -> None:
        self.notes = notes
        self.docs = self._docs()
        self.work = sorted(p for p in (notes / "work").glob("w[0-9]*") if p.is_dir())
        self.followups = sorted((notes / "followups").glob("f[0-9]*.md"))
        self.questions = sorted((notes / "questions").glob("q[0-9]*.md"))
        self.other = {
            sub: sorted(f for f in (notes / "other" / sub).rglob("*") if f.is_file())
            for sub in ("in", "out")
            if (notes / "other" / sub).exists()
        }
        self.urls: dict[str, str] = {}
        for d in self.docs:
            self.urls[d["id"]] = d["page"]
        self._decisions: dict[str, dict[str, tuple[str, str]]] = {}
        self._states: dict[str, dict] = {}
        for w in self.work:
            self.urls[w.name[:4]] = self.page_of(w / "brief.md")
        for f in self.followups:
            self.urls[f.name[:4]] = self.page_of(f)
        for q in self.questions:
            self.urls[q.name[:4]] = self.page_of(q)

    def _docs(self) -> list[dict]:
        out = []
        for p in sorted((self.notes / "docs").glob("d[0-9]*")):
            if p.suffix == ".md" and p.is_file():
                meta, body = frontmatter(p.read_text(errors="replace"))
                out.append(
                    {
                        "id": p.name[:4],
                        "title": split_title(body, p.stem)[0],
                        "page": self.page_of(p),
                        "status": re.sub(r"^status:\s*", "", meta.get("status", "")),
                        "src": p,
                    }
                )
                continue
            page = p / "index.html" if p.is_dir() else p
            if not page.is_file() or page.suffix != ".html":
                continue
            text = page.read_text(errors="replace")
            title = re.search(r"<title>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
            status = re.search(
                r"<p[^>]*class=\"[^\"]*\bstatus\b[^\"]*\"[^>]*>(.*?)</p>",
                text,
                re.DOTALL | re.IGNORECASE,
            )
            status_text = re.sub(
                r"^status:\s*", "", strip_tags(status[1]) if status else ""
            )
            out.append(
                {
                    "id": p.name[:4],
                    "title": strip_tags(title[1]) if title else p.stem,
                    "page": page.relative_to(self.notes).as_posix(),
                    "status": status_text,
                    "src": page,
                }
            )
        return out

    def decisions(self, work: str) -> dict[str, tuple[str, str]]:
        """key -> (choice, date) from a work item's decisions.md, the last line per key wins"""
        if work not in self._decisions:
            found: dict[str, tuple[str, str]] = {}
            for d in (self.notes / "work").glob(f"{work}-*"):
                f = d / "decisions.md"
                for m in DECISION_LINE.finditer(f.read_text() if f.is_file() else ""):
                    found[m["key"]] = (m["choice"], m["date"])
            self._decisions[work] = found
        return self._decisions[work]

    def state(self, w: Path) -> dict:
        """item_state of a work item, worked out once per regeneration"""
        if w.name not in self._states:
            self._states[w.name] = item_state(self, w)
        return self._states[w.name]

    def page_of(self, src: Path) -> str:
        """where a markdown file's rendered page lives, relative to .notes/"""
        rel = src.relative_to(self.notes).with_suffix(".html")
        return f"{PAGES}/{rel.as_posix()}"

    def source_of(self, generated: Path) -> Path:
        """page_of and write_portable backwards: the file or folder a generated one comes
        from, _pages/x.html from x.md, _out/x from other/out/x"""
        top, *rest = generated.relative_to(self.notes).parts
        if top == OUT:
            return self.notes.joinpath("other", "out", *rest)
        src = self.notes.joinpath(*rest)
        return src.with_suffix(".md") if generated.suffix == ".html" else src

    def href(self, target: str, from_page: str) -> str:
        """a link from one page to another, both relative to .notes/"""
        base = Path(from_page).parent
        return quote(Path(*([".."] * len(base.parts)), target).as_posix())


# a work item's state: what matej does next, what waits on him, its branches in the project


def split_section(body: str, heading: str) -> tuple[str, str]:
    """the lines under a `## heading` up to the next `## `, stripped, and the body
    without that section"""
    m = re.search(
        rf"^##\s+{re.escape(heading)}\b[^\n]*\n(.*?)(?=^##\s|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    return (m[1].strip(), body[: m.start()] + body[m.end() :]) if m else ("", body)


def in_main(repo: Path, branch: str) -> bool:
    """an ancestor of main, or every commit's patch is in main: matej re-signs a branch
    before merging it, which changes its shas"""
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", branch, "main"],
        check=False,
        capture_output=True,
    ).returncode
    if ancestor != 1:
        return ancestor == 0
    cherry = git(repo, "cherry", "main", branch, check=False).splitlines()
    return bool(cherry) and not any(line.startswith("+") for line in cherry)


def branches(notes: Path, work: str) -> list[tuple[str, str, bool]]:
    """(branch, short sha, in main) for every local branch under the work id in the
    project's git; .notes/ sits at the project's root"""
    repo = notes.parent
    out = git(
        repo,
        "for-each-ref",
        "--format=%(refname:short) %(objectname) %(objectname:short)",
        f"refs/heads/{work}/",
        check=False,
    )
    if not out:
        return []
    # a tip on main's own line is a branch just cut, with nothing of its own yet;
    # matej merges with --no-ff, so a merged branch's tip sits off that line
    mainline = set(git(repo, "rev-list", "--first-parent", "main", check=False).split())
    return [
        (name, short, sha not in mainline and in_main(repo, name))
        for name, sha, short in (line.split() for line in out.splitlines())
    ]


def item_state(site: "Site", w: Path) -> dict:
    """what a work item waits on, worked out from its files and the project's branches"""
    work = w.name[:4]
    brief = w / "brief.md"
    body = frontmatter(brief.read_text(errors="replace"))[1] if brief.exists() else ""
    title = split_title(body, w.name[5:])[0]
    chosen = site.decisions(work)
    waiting = [
        (key, f)
        for f in sorted(w.rglob("*.md"))
        for key in decide_blocks(f.read_text(errors="replace"))
        if key not in chosen
    ]
    found = branches(site.notes, work)
    # a prototype branch never lands, so it says nothing about the item being done
    real = [merged for b, _, merged in found if not b.endswith("prototype")]
    landed = bool(real) and all(real)
    flags = []
    if waiting:
        flags.append(("warn", f"{len(waiting)} to decide"))
    if landed:
        flags.append(("bad", "merged, not closed out"))
    if unmerged := real.count(False):
        flags.append(("info", f"{unmerged} branch{'es' if unmerged > 1 else ''} open"))
    last = git(site.notes, "log", "-1", "--format=%cs", "--", str(w), check=False)
    return {
        "title": title,
        "move": split_section(body, "Your move")[0],
        "next": split_section(body, "Next")[0],
        "landed": landed,
        "waiting": waiting,
        "branches": found,
        "last": last.strip(),
        "flags": flags,
    }


def page(site: Site, path: str, title: str, body: str) -> str:
    css = site.href("notes.css", path)
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n{ICON}\n"
        f'<link rel="stylesheet" href="{css}">\n</head>\n'
        f'<body>\n<main class="page">\n{body}\n</main>\n</body>\n</html>\n'
    )


# markdown, the small subset notes are written in


def inline(text: str, site: Site, at: str) -> str:
    out, last = [], 0
    for m in re.finditer(r"`([^`]+)`", text):
        out.append(inline_plain(text[last : m.start()], site, at))
        out.append(f"<code>{html.escape(m[1])}</code>")
        last = m.end()
    out.append(inline_plain(text[last:], site, at))
    return "".join(out)


def link_href(target: str, site: Site, at: str) -> str:
    """a relative link in a markdown file points from that file; its page sits under
    _pages/, so the link is rebased, and a .md target goes to its rendered page"""
    if re.match(r"([a-z][a-z0-9+.-]*:|/|#)", target) or not at.startswith(f"{PAGES}/"):
        return target
    path, _, frag = target.partition("#")
    src_dir = posixpath.dirname(at.removeprefix(f"{PAGES}/"))
    rel = posixpath.normpath(posixpath.join(src_dir, path))
    if rel.endswith(".md") and not rel.startswith("../"):
        rel = f"{PAGES}/{rel.removesuffix('.md')}.html"
    slash = "/" if path.endswith("/") else ""
    return site.href(rel, at) + slash + (f"#{frag}" if frag else "")


def inline_plain(text: str, site: Site, at: str) -> str:
    links: list[str] = []

    def keep(s: str) -> str:
        links.append(s)
        return f"\x00{len(links) - 1}\x00"

    text = MD_LINK.sub(
        lambda m: keep(
            f'<a href="{html.escape(link_href(m[2], site, at))}">{html.escape(m[1])}</a>'
        ),
        text,
    )
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def id_link(m: re.Match) -> str:
        url = site.urls.get(m[1])
        return f'<a href="{site.href(url, at)}">{m[1]}</a>' if url else m[1]

    text = ID_TOKEN.sub(id_link, text)
    return re.sub(r"\x00(\d+)\x00", lambda m: links[int(m[1])], text)


# gfm pipe tables: a header row, a row of dashes, then body rows up to a line without a pipe
PIPE = re.compile(r"(?<!\\)\|")
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
ALIGN = {(True, True): "center", (False, True): "right", (True, False): "left"}


def table_cells(line: str) -> list[str]:
    s = line.strip()
    s = s.removeprefix("|")
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in PIPE.split(s)]


def table_start(lines: list[str], i: int) -> list[str] | None:
    """the column alignments if a table starts at lines[i], else None"""
    if i + 1 >= len(lines) or not (PIPE.search(lines[i]) and PIPE.search(lines[i + 1])):
        return None
    seps = table_cells(lines[i + 1])
    if len(table_cells(lines[i])) != len(seps):
        return None
    if not all(SEPARATOR_CELL.match(c) for c in seps):
        return None
    return [ALIGN.get((c[0] == ":", c[-1] == ":"), "") for c in seps]


def table_row(line: str, aligns: list[str], tag: str, site: Site, at: str) -> str:
    # short rows are padded, extra cells dropped, as gfm does
    cells = (table_cells(line) + [""] * len(aligns))[: len(aligns)]
    row = []
    for cell, align in zip(cells, aligns):
        style = f' style="text-align: {align}"' if align else ""
        row.append(f"<{tag}{style}>{inline(cell, site, at)}</{tag}>")
    return f"<tr>{''.join(row)}</tr>"


# decide blocks: a fence ```decide <key> whose lines are options, `a) title` or `a*) title` for the
# recommended one, each followed by its text; served by notes.py a click records the choice
DECIDE_FENCE = re.compile(r"^\s*```decide\s+([a-z0-9-]{1,40})\s*$")
OPTION_LINE = re.compile(r"^([a-z0-9]{1,12})(\*?)\)\s+(.+)$")
DECISION_LINE = re.compile(
    r"^- (?P<date>\d{4}-\d{2}-\d{2}) (?P<key>[a-z0-9-]{1,40}): (?P<choice>[a-z0-9]{1,12})\b",
    re.MULTILINE,
)


def decide_options(lines: list[str]) -> list[tuple[str, bool, str, list[str]]]:
    """(key, recommended, title, text lines) per option of one decide block"""
    options: list[tuple[str, bool, str, list[str]]] = []
    for line in lines:
        if m := OPTION_LINE.match(line.strip()):
            options.append((m[1], bool(m[2]), m[3], []))
        elif options and line.strip():
            options[-1][3].append(line.strip())
    return options


def decide_blocks(text: str) -> dict[str, list[str]]:
    """decide key -> its option keys, for every decide block in a markdown text"""
    found: dict[str, list[str]] = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if m := DECIDE_FENCE.match(line):
            body = []
            for rest in lines[i + 1 :]:
                if rest.lstrip().startswith("```"):
                    break
                body.append(rest)
            found[m[1]] = [o[0] for o in decide_options(body)]
    return found


def decide_block(key: str, lines: list[str], site: Site, at: str) -> str:
    e = html.escape
    options = decide_options(lines)
    work = m[1] if (m := re.match(r"_pages/work/(w\d{3})-", at)) else ""
    chosen, day = site.decisions(work).get(key, ("", "")) if work else ("", "")
    boxes = []
    for opt, rec, title, text in options:
        cls = " ".join(
            c
            for c in ("option", rec and "recommended", opt == chosen and "chosen")
            if c
        )
        tags = ' <span class="tag good">recommended</span>' if rec else ""
        if opt == chosen:
            tags += f' <span class="tag info">chosen {e(day)}</span>'
        body = f"<p>{inline(' '.join(text), site, at)}</p>" if text else ""
        button = (
            f'<button name="choice" value="{e(opt)}">choose {e(opt)}</button>'
            if work
            else ""
        )
        boxes.append(
            f'<div class="{cls}"><p class="option-head"><strong>{e(opt)} · '
            f"{inline(title, site, at)}</strong>{tags}</p>{body}{button}</div>"
        )
    if not work:
        return f'<div class="decide">{"".join(boxes)}</div>'
    action = site.href("decide", at)
    hidden = (
        f'<input type="hidden" name="work" value="{work}">'
        f'<input type="hidden" name="key" value="{e(key)}">'
    )
    paste = "|".join(o[0] for o in options)
    return (
        f'<form class="decide" id="decide-{e(key)}" method="post" action="{action}">'
        f"{hidden}{''.join(boxes)}</form>"
        f'<p class="sub decide-paste">not served by notes.py: tell the lead '
        f"<code>{work} {e(key)}: {e(paste)}</code></p>"
    )


def markdown(text: str, site: Site, at: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    para: list[str] = []
    # open lists as (indent, tag)
    lists: list[tuple[int, str]] = []
    item_open = False

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para), site, at)}</p>")
            para.clear()

    def close_lists(to: int = -1) -> None:
        nonlocal item_open
        while lists and lists[-1][0] > to:
            out.append(f"</li></{lists.pop()[1]}>")
        item_open = bool(lists)

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            flush_para()
            close_lists()
            indent = len(line) - len(line.lstrip())
            code = []
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                code.append(lines[i][indent:])
                i += 1
            if m := DECIDE_FENCE.match(line):
                out.append(decide_block(m[1], code, site, at))
            else:
                out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
            i += 1
            continue
        if not line.strip():
            flush_para()
            i += 1
            continue
        if m := re.match(r"^(#{1,4})\s+(.*)$", line):
            flush_para()
            close_lists()
            level = min(len(m[1]) + 1, 4)
            out.append(f"<h{level}>{inline(m[2], site, at)}</h{level}>")
            i += 1
            continue
        if aligns := table_start(lines, i):
            flush_para()
            close_lists()
            head = table_row(line, aligns, "th", site, at)
            i += 2
            body = []
            while i < len(lines) and PIPE.search(lines[i]):
                body.append(table_row(lines[i], aligns, "td", site, at))
                i += 1
            tbody = f"<tbody>{''.join(body)}</tbody>" if body else ""
            out.append(
                f'<div class="table"><table><thead>{head}</thead>{tbody}</table></div>'
            )
            continue
        if m := re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line):
            flush_para()
            indent, tag = len(m[1]), "ol" if m[2][0].isdigit() else "ul"
            if not lists or indent > lists[-1][0]:
                out.append(f"<{tag}><li>")
                lists.append((indent, tag))
            else:
                close_lists(indent)
                # the other kind of list at the same indent ends this one and starts its own
                if lists and lists[-1][0] == indent and lists[-1][1] != tag:
                    close_lists(indent - 1)
                if lists and lists[-1][0] == indent:
                    out.append("</li><li>")
                else:
                    out.append(f"<{tag}><li>")
                    lists.append((indent, tag))
            item = [m[3]]
            i += 1
            # continuation lines belong to the item
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"^\s*([-*]|\d+\.)\s+|^\s*```|^#{1,4}\s", lines[i])
                and not table_start(lines, i)
            ):
                item.append(lines[i].strip())
                i += 1
            out.append(inline(" ".join(item), site, at))
            continue
        if lists and line.startswith(" "):
            out.append(" " + inline(line.strip(), site, at))
            i += 1
            continue
        close_lists()
        para.append(line.strip())
        i += 1
    flush_para()
    close_lists()
    return "\n".join(out)


def render_md(site: Site, src: Path, kind: str) -> None:
    at = site.page_of(src)
    meta, body = frontmatter(src.read_text(errors="replace"))
    title, body = split_title(body, src.stem)
    e = html.escape
    item_id = next((p[:4] for p in src.parts if re.match(r"[dwfq]\d{3}-", p)), "")
    status = ""
    if kind == "doc":
        # a doc's type, date and status go where an html doc has them, not in the meta row
        kind = " · ".join(x for x in (meta.pop("type", ""), meta.pop("date", "")) if x)
        text = meta.pop("status", "")
        cls = next(
            (
                c
                for p, c in (
                    ("current", "current"),
                    ("partly stale", "stale"),
                    ("superseded", "superseded"),
                )
                if text.startswith(p)
            ),
            "",
        )
        status = f'<p class="status {cls}">status: {inline(text, site, at)}</p>'
    eyebrow = " · ".join(x for x in (item_id, kind) if x)
    parts = [
        f'<nav class="back"><a href="{site.href("index.html", at)}">← notes</a></nav>',
        "<header>",
        f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else "",
        f"<h1>{e(title)}</h1>",
        status,
    ]
    if meta:
        dl = "".join(
            f"<div><dt>{e(k)}</dt><dd>{inline(v, site, at)}</dd></div>"
            for k, v in meta.items()
        )
        parts.append(f'<dl class="md-meta">{dl}</dl>')
    parts.append("</header>")
    if kind == "work" and src == site.notes / "work" / src.parent.name / "brief.md":
        # the box shows the move on top; the brief keeps the section for the lead and agents
        parts.append(move_box(site, src.parent, at))
        body = split_section(body, "Your move")[1]
    parts.append(markdown(body, site, at))
    if kind == "work":
        files = []
        for f in sorted(src.parent.rglob("*")):
            if not f.is_file() or f == src:
                continue
            target = site.page_of(f) if f.suffix == ".md" else f.relative_to(site.notes)
            files.append(f'<a href="{site.href(str(target), at)}">{e(f.name)}</a>')
        if files:
            parts.append(f'<p class="files">files: {" · ".join(files)}</p>')
    write_whole(
        site.notes / at, page(site, at, title, "\n".join(p for p in parts if p))
    )


def tags(flags: list[tuple[str, str]]) -> str:
    return " ".join(f'<span class="tag {c}">{html.escape(t)}</span>' for c, t in flags)


def move_box(site: Site, w: Path, at: str) -> str:
    """the top of a work item's page: matej's move, the decisions waiting, the branches"""
    e = html.escape
    st = site.state(w)
    rows = [
        markdown(st["move"], site, at)
        if st["move"]
        else '<p class="sub">no move written: the lead adds <code>## Your move</code>'
        " to the brief</p>"
    ]
    if st["waiting"]:
        links = " · ".join(
            f'<a href="{site.href(site.page_of(src), at)}#decide-{e(key)}">{e(key)}</a>'
            for key, src in st["waiting"]
        )
        rows.append(f"<p><strong>to decide:</strong> {links}</p>")
    if st["branches"]:
        tag = {
            True: '<span class="tag good">in main</span>',
            False: '<span class="tag muted">not in main</span>',
        }
        listed = " · ".join(
            f"<code>{e(b)}</code> {sha} {tag[merged]}"
            for b, sha, merged in st["branches"]
        )
        rows.append(f'<p class="sub">branches: {listed}</p>')
    if st["flags"]:
        rows.append(f"<p>{tags(st['flags'])}</p>")
    return f'<section class="callout info move"><h2>Your move</h2>{"".join(rows)}</section>'


def write_portable(site: Site) -> None:
    """other/out/ as it leaves .notes/: css inlined, no back link to an index it won't have"""
    src = site.notes / "other" / "out"
    style = f"<style>\n{CSS.read_text()}</style>"
    for f in site.other.get("out", []):
        target = site.notes / OUT / f.relative_to(src)
        if f.suffix != ".html":
            write_whole(target, f.read_bytes())
            continue
        # the nav goes before the css comes in: its header comment shows a nav too
        text = BACK_NAV.sub("", f.read_text(errors="replace"), count=1)
        write_whole(target, CSS_LINK.sub(lambda _: style, text, count=1))


def write_whole(path: Path, data: str | bytes) -> None:
    """write beside path, then rename over it: readers see the old file or the new one"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{secrets.token_hex(4)}.partial")
    try:
        tmp.write_bytes(data) if isinstance(data, bytes) else tmp.write_text(data)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def prune(site: Site) -> None:
    """generated files and folders whose source is gone or changed kind, and the partial
    files of crashed builds; another build may be writing alongside, so its partials stay"""
    notes = site.notes
    # notes.css was just written: its mtime is now by the clock that stamps the partials
    now = (notes / "notes.css").stat().st_mtime
    found = [
        *notes.glob(".*.partial"),
        *(notes / PAGES).rglob("*"),
        *(notes / OUT).rglob("*"),
    ]
    # deepest first, so a folder is looked at once its contents are gone
    for f in sorted(found, reverse=True):
        try:
            if PARTIAL.match(f.name):
                if now - f.lstat().st_mtime > PARTIAL_AGE:
                    f.unlink()
            elif f.is_dir():
                if not site.source_of(f).is_dir() and not any(f.iterdir()):
                    f.rmdir()
            elif not site.source_of(f).is_file():
                f.unlink()
        except FileNotFoundError:
            # another build removed or renamed it first
            pass


def write_index(notes: Path) -> None:
    ensure_gitignore(notes)
    write_whole(notes / "notes.css", CSS.read_text())
    site = Site(notes)
    prune(site)

    write_portable(site)
    for d in site.docs:
        if d["src"].suffix == ".md":
            render_md(site, d["src"], "doc")
    for f in site.followups:
        render_md(site, f, "follow-up")
    for q in site.questions:
        render_md(site, q, "question")
    for w in site.work:
        for f in sorted(w.rglob("*.md")):
            render_md(site, f, "work")
    for files in site.other.values():
        for f in files:
            if f.suffix == ".md":
                render_md(site, f, "other")

    e = html.escape

    def section(name: str, rows: list[str], empty: str) -> str:
        head = f'<h2>{name} <span class="count">{len(rows)}</span></h2>'
        if not rows:
            return f'{head}<p class="empty">{empty}</p>'
        return f'{head}<ul class="rows">{"".join(rows)}</ul>'

    def row(item_id: str, href: str, title: str, meta: str, line: str = "") -> str:
        return (
            f'<li><span class="id">{e(item_id)}</span>'
            f'<span class="title"><a href="{href}">{e(title)}</a>{line}</span>'
            f'<span class="meta">{meta}</span></li>'
        )

    # matej reads work items and his questions; docs, follow-ups and other/ are the lead's
    # and the agents' side, rendered so a link from a work item still opens
    work = []
    for w in site.work:
        st = site.state(w)
        meta = f'{tags(st["flags"])} <span class="sub">{e(st["last"])}</span>'
        line = ""
        if st["move"]:
            # links in the move point from the brief, so here they keep only their text
            first = re.sub(r"^[-*]\s+", "", st["move"].splitlines()[0])
            first = MD_LINK.sub(r"\1", first)
            line = f'<span class="move sub">{inline(first, site, "index.html")}</span>'
        work.append(
            row(w.name[:4], quote(site.urls[w.name[:4]]), st["title"], meta, line)
        )
    questions = []
    for q in site.questions:
        meta, body = frontmatter(q.read_text(errors="replace"))
        title, _ = split_title(body, q.stem)
        created = e(meta.get("created", ""))
        questions.append(row(q.name[:4], quote(site.page_of(q)), title, created))

    project = notes.parent.name
    body = "\n".join(
        [
            # under serve this is the hub, under a plain http.server it is this index
            '<nav class="back"><a href="/">← all notes</a></nav>',
            '<header class="index-head">',
            f"<h1>{e(project)} notes</h1>",
            (
                f"<p>{len(site.work)} in flight · {len(site.questions)} open questions · "
                f"generated {datetime.now().astimezone().date()}</p>"
            ),
            "</header>",
            '<div class="index">',
            section("Work in flight", work, "nothing in flight"),
            section("Your questions", questions, "no open questions"),
            "</div>",
        ]
    )
    write_whole(
        notes / "index.html", page(site, "index.html", f"{project} notes", body)
    )


# status: what is open and what waits, for a fresh lead session


def status(notes: Path) -> None:
    site = Site(notes)
    for w in site.work:
        st = site.state(w)
        print(f"{w.name[:4]} {st['title']}  (notes touched {st['last']})")
        for _, text in st["flags"]:
            print(f"  ! {text}")
        for label in ("move", "next"):
            if lines := st[label].splitlines():
                more = f" (+{len(lines) - 1} lines)" if len(lines) > 1 else ""
                print(f"  {label}: {lines[0][:160]}{more}")
        for key, src in st["waiting"]:
            print(f"  decide {key} in {src.relative_to(notes)}")
        for b, sha, merged in st["branches"]:
            print(f"  branch {b} {sha} {'in main' if merged else 'not in main'}")
    states = [frontmatter(f.read_text(errors="replace"))[0] for f in site.followups]
    open_fs = sum(1 for m in states if m.get("status", "open").startswith("open"))
    print(
        f"follow-ups {open_fs} open · questions {len(site.questions)} · docs {len(site.docs)}"
    )
    # superseded is a doc's normal end; stale or missing status lines need the lead
    for label, test in (
        ("partly stale", lambda st: st.startswith("partly stale")),
        ("no status line", lambda st: not st),
    ):
        if ids := [d["id"] for d in site.docs if test(d["status"])]:
            print(f"  docs {label}: {', '.join(ids)}")


# file: an agent's final reply into its work item, verbatim from the transcript

HARNESS_PREFIX = re.compile(r"^\[harness:[^\]]*\]\s*")


def final_reply(transcript: Path) -> str:
    """the text of the agent's last end_turn message, as the task notification carries it
    (the notification html-escapes it and may put a harness warning before it)"""
    # one message can span several jsonl records sharing its id
    msgs: list[tuple[str, str, list[str]]] = []
    for line in transcript.open():
        record = json.loads(line)
        if record.get("type") != "assistant":
            continue
        m = record.get("message") or {}
        texts = [
            b["text"]
            for b in m.get("content") or []
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        if msgs and msgs[-1][0] == m.get("id"):
            msg_id, stop, prev = msgs.pop()
            msgs.append((msg_id, m.get("stop_reason") or stop, prev + texts))
        else:
            msgs.append((m.get("id"), m.get("stop_reason"), texts))
    done = [texts for _, stop, texts in msgs if stop == "end_turn" and texts]
    if not done:
        sys.exit(f"{transcript}: no finished reply in it")
    return HARNESS_PREFIX.sub("", "\n\n".join(done[-1]).strip())


def find_transcript(ref: str) -> Path:
    """the notification's output-file (a symlink to the transcript), a jsonl, or an agent id"""
    path = Path(ref).expanduser()
    if path.exists():
        return path.resolve()
    if not re.fullmatch(r"[0-9a-z]{6,40}", ref):
        sys.exit(f"{ref}: neither a file nor an agent id")
    bases = (
        [Path(os.environ["CLAUDE_CONFIG_DIR"])]
        if "CLAUDE_CONFIG_DIR" in os.environ
        else []
    )
    bases += [Path.home() / ".claude", Path.home() / ".config" / "claude"]
    for base in bases:
        hits = sorted((base / "projects").glob(f"*/*/subagents/agent-{ref}.jsonl"))
        if hits:
            return max(hits, key=lambda h: h.stat().st_mtime)
    sys.exit(f"no transcript for agent {ref}")


def file_reply(notes: Path, work: str, part: str, ref: str, checked: str) -> None:
    dirs = [d for d in (notes / "work").glob(f"{work}-*") if d.is_dir()]
    if not re.fullmatch(r"w\d{3}", work) or len(dirs) != 1:
        sys.exit(f"no work item {work}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", part):
        sys.exit(f"part {part!r} is not lowercase kebab")
    out = dirs[0] / f"report-{part}.md"
    if out.exists():
        sys.exit(f"{out} exists; pick another part name")
    reply = final_reply(find_transcript(ref))
    day = datetime.now().astimezone().date().isoformat()
    out.write_text(
        f"# {work} report: {part} ({day})\n\nLead checked: {checked.strip()}\n\n"
        f"## Reply as it came\n\n{reply}\n"
    )
    print(out.relative_to(notes), f"{len(reply)} chars")


# serve: every project's notes on one port


SKIP_DIRS = {"node_modules", "target", "dist", "build", "vendor", "__pycache__"}


def find_notes(roots: list[Path], depth: int = 6) -> dict[str, Path]:
    """url prefix (path relative to its root) -> .notes dir, for every project under roots"""
    found: dict[str, Path] = {}

    def walk(d: Path, root: Path, left: int) -> None:
        notes = d / ".notes"
        if notes.is_dir() and (notes / "docs").is_dir():
            # a root that is itself a project goes by its name, not "."
            found[d.name if d == root else d.relative_to(root).as_posix()] = notes
            # a project's subdirectories are its code, even when the project is a root
            return
        # a repo's own subdirectories are its code, not more projects
        if left == 0 or ((d / ".git").exists() and d != root):
            return
        try:
            children = sorted(d.iterdir())
        except OSError:
            return
        for c in children:
            skip = c.name.startswith(".") or c.name in SKIP_DIRS
            if c.is_dir() and not c.is_symlink() and not skip:
                walk(c, root, left - 1)

    for root in roots:
        if root.is_dir():
            walk(root, root, depth)
    return found


def hub_page(title: str, body: str) -> str:
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n{ICON}\n"
        '<link rel="stylesheet" href="/notes.css">\n</head>\n'
        f'<body>\n<main class="page">\n{body}\n</main>\n</body>\n</html>\n'
    )


def search_form(action: str, q: str = "") -> str:
    return (
        f'<form class="search" action="{action}" role="search">'
        f'<input type="search" name="q" value="{html.escape(q)}" '
        'placeholder="search this project\'s notes" aria-label="search notes">'
        "</form>"
    )


# filters the hub's project rows as you type, nothing leaves the page
FILTER_BOX = (
    '<input class="filter" type="search" placeholder="filter projects" '
    'aria-label="filter projects" autofocus>'
)
FILTER_SCRIPT = """<script>
const box = document.querySelector("input.filter");
const rows = [...document.querySelectorAll(".rows.hub li")];
box.addEventListener("input", () => {
  const words = box.value.toLowerCase().split(/\\s+/).filter(Boolean);
  for (const r of rows) {
    const name = r.dataset.name;
    r.hidden = !words.every((w) => name.includes(w));
  }
  document.querySelector(".hub-empty").hidden = rows.some((r) => !r.hidden);
});
box.addEventListener("keydown", (e) => {
  const first = rows.find((r) => !r.hidden);
  if (e.key === "Enter" && first) location.href = first.querySelector("a").href;
});
</script>"""


def hub(projects: dict[str, Path]) -> str:
    e = html.escape
    rows = []
    for prefix, notes in sorted(projects.items()):
        questions = len(list((notes / "questions").glob("q[0-9]*.md")))
        followups = len(list((notes / "followups").glob("f[0-9]*.md")))
        work = len([p for p in (notes / "work").glob("w[0-9]*") if p.is_dir()])
        docs = len(list((notes / "docs").glob("d[0-9]*")))
        last = git(notes, "log", "-1", "--format=%cs", check=False).strip()
        meta = f"{docs} docs · {work} in flight · {followups} follow-ups · {questions} open · {last or 'no commits'}"
        rows.append(
            f'<li data-name="{e(prefix.lower())}">'
            f'<span class="title"><a href="/{quote(prefix)}/">{e(prefix)}</a></span>'
            f'<span class="meta">{meta}</span></li>'
        )
    body = (
        '<header class="index-head"><h1>notes</h1>'
        f"<p>{len(projects)} projects · generated {datetime.now().astimezone().date()}</p></header>"
        + (FILTER_BOX if rows else "")
        + '<div class="index"><h2>Projects</h2>'
        + (
            f'<ul class="rows hub">{"".join(rows)}</ul>'
            '<p class="empty hub-empty" hidden>no project matches</p>'
            if rows
            else '<p class="empty">no .notes/ found</p>'
        )
        + "</div>"
        # after the rows, so the script finds them
        + (FILTER_SCRIPT if rows else "")
    )
    return hub_page("notes", body)


def page_text(page: str) -> str:
    """the readable text of an html page, without its chrome, words kept apart"""
    flags = re.DOTALL | re.IGNORECASE
    page = re.sub(r"<(style|script|svg|nav|title)\b.*?</\1>", " ", page, flags=flags)
    return html.unescape(re.sub(r"<[^>]+>", " ", page))


def searchable(notes: Path) -> list[tuple[str, str, str, str]]:
    """(id, title, url relative to .notes/, plain text) for every page worth searching"""
    site = Site(notes)
    out = []
    for d in site.docs:
        text = d["src"].read_text(errors="replace")
        if d["src"].suffix == ".html":
            text = page_text(text)
        out.append((d["id"], d["title"], d["page"], text))
    mds = [
        *site.followups,
        *site.questions,
        *(f for w in site.work for f in sorted(w.rglob("*.md"))),
    ]
    mds += [f for files in site.other.values() for f in files if f.suffix == ".md"]
    for f in mds:
        _, body = frontmatter(f.read_text(errors="replace"))
        title, _ = split_title(body, f.stem)
        item = next((p[:4] for p in f.parts if re.match(r"[dwfq]\d{3}-", p)), "")
        out.append((item, title, site.page_of(f), body))
    for files in site.other.values():
        for f in files:
            if f.suffix == ".html":
                text = page_text(f.read_text(errors="replace"))
                out.append(("", f.name, f.relative_to(notes).as_posix(), text))
    return out


def search(prefix: str, notes: Path, q: str) -> str:
    e = html.escape
    terms = [t.lower() for t in q.split() if t]
    hits = []
    for item, title, url, text in searchable(notes) if terms else []:
        low_title, low = title.lower(), " ".join(text.split()).lower()
        if not all(t in low_title or t in low for t in terms):
            continue
        flat = " ".join(text.split())
        # centre on the whole phrase if it occurs, else on the rarest word
        at = low.find(" ".join(terms))
        if at < 0:
            rarest = min((t for t in terms if t in low), key=low.count, default="")
            at = max(low.find(rarest), 0) if rarest else 0
        start = max(0, at - 80)
        snippet = e(("…" if start else "") + flat[start : at + 160] + "…")
        for t in sorted(set(terms), key=len, reverse=True):
            snippet = re.sub(
                f"({re.escape(e(t))})", r"<mark>\1</mark>", snippet, flags=re.IGNORECASE
            )
        score = sum(t in low_title for t in terms) * 100 + sum(
            low.count(t) for t in terms
        )
        hits.append((score, item, title, url, snippet))
    write_index(notes)
    hits.sort(key=lambda h: -h[0])
    rows = "".join(
        f'<li><span class="id">{e(item)}</span><span class="title">'
        f'<a href="{quote(url)}">{e(title)}</a>'
        f'<span class="snippet">{snippet}</span></span></li>'
        for _, item, title, url, snippet in hits
    )
    found = (
        f'<ul class="rows results">{rows}</ul>'
        if rows
        else '<p class="empty">nothing found</p>'
    )
    body = (
        '<nav class="back"><a href="./">← notes</a></nav>'
        f'<header class="index-head"><h1>{e(prefix)}: search</h1>'
        f"<p>{len(hits)} results for “{e(q)}”</p></header>"
        + search_form("search", q)
        + f'<div class="index">{found}</div>'
    )
    return hub_page(f"{q} · {prefix} notes", body)


LOOPBACK = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}
LOCAL_NAMES = {"127.0.0.1", "localhost", "::1"}


def serve(roots: list[Path], host: str, port: int) -> None:
    import http.server
    import threading
    from urllib.parse import parse_qs, unquote, urlsplit

    # one decision append and commit at a time
    write_lock = threading.Lock()
    # a scan can take a second under a big root: done at start and on each hub visit
    projects = find_notes(roots)

    def rescan() -> dict[str, Path]:
        nonlocal projects
        projects = find_notes(roots)
        return projects

    def lookup(path: str) -> tuple[str, Path] | None:
        """the project a path is under and its .notes/, by the last scan; a miss rescans
        once, for a project added since"""

        def longest(found: dict[str, Path]) -> tuple[str, Path] | None:
            under = [p for p in found if path == f"/{p}" or path.startswith(f"/{p}/")]
            prefix = max(under, key=len, default=None)
            return (prefix, found[prefix]) if prefix is not None else None

        hit = longest(projects)
        if hit is None or not hit[1].is_dir():
            hit = longest(rescan())
        return hit

    class Handler(http.server.SimpleHTTPRequestHandler):
        def guess_type(self, path: str) -> str:
            if str(path).endswith(".md"):
                return "text/plain; charset=utf-8"
            return super().guess_type(path)

        def send_text(self, body: str, ctype: str) -> None:
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            path = unquote(urlsplit(self.path).path)
            if path in ("/", "/index.html"):
                return self.send_text(hub(rescan()), "text/html; charset=utf-8")
            if path == "/notes.css":
                return self.send_text(CSS.read_text(), "text/css; charset=utf-8")
            hit = lookup(path)
            if hit is None:
                return self.send_error(404, "no such project")
            prefix, notes = hit
            if path == f"/{prefix}":
                self.send_response(301)
                self.send_header("Location", f"/{quote(prefix)}/")
                self.end_headers()
                return None
            rest = path[len(prefix) + 2 :]
            if rest == "search":
                q = parse_qs(urlsplit(self.path).query).get("q", [""])[0]
                body = search(prefix, notes, q)
                return self.send_text(body, "text/html; charset=utf-8")
            if rest in ("", "index.html"):
                # rebuilt on every visit, so a session that forgot to regenerate never shows stale;
                # the search box only works under serve, so it is added here, not in the file
                write_index(notes)
                page = (notes / "index.html").read_text()
                page = page.replace("</header>", "</header>" + search_form("search"), 1)
                return self.send_text(page, "text/html; charset=utf-8")
            self.serve_from = notes
            self.path = "/" + rest
            return super().do_GET()

        def do_POST(self) -> None:
            # <project>/decide: one click in a decide block, appended to work/wNNN-*/decisions.md
            host = urlsplit(f"//{self.headers.get('Host', '')}").hostname
            if self.client_address[0] not in LOOPBACK or host not in LOCAL_NAMES:
                return self.send_error(403, "local only")
            # browsers send it on every post; a client without it (curl) is not a page
            if self.headers.get("Sec-Fetch-Site", "same-origin") != "same-origin":
                return self.send_error(403, "cross-site")
            path = unquote(urlsplit(self.path).path)
            hit = lookup(path)
            if hit is None or path != f"/{hit[0]}/decide":
                return self.send_error(404)
            prefix, notes = hit
            length = self.headers.get("Content-Length", "")
            n = min(int(length), 4096) if length.isdigit() else 0
            form = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
            work, key, choice = (form.get(f, "") for f in ("work", "key", "choice"))
            if not (
                re.fullmatch(r"w\d{3}", work)
                and re.fullmatch(r"[a-z0-9-]{1,40}", key)
                and re.fullmatch(r"[a-z0-9]{1,12}", choice)
            ):
                return self.send_error(400, "bad fields")
            dirs = [d for d in (notes / "work").glob(f"{work}-*") if d.is_dir()]
            if len(dirs) != 1:
                return self.send_error(404, "no such work item")
            # only an option the work item's own pages offer for that key
            offered: set[str] = set()
            for f in dirs[0].rglob("*.md"):
                offered.update(
                    decide_blocks(f.read_text(errors="replace")).get(key, [])
                )
            if choice not in offered:
                return self.send_error(400, "not an option of that decision")
            day = datetime.now().astimezone().date().isoformat()
            with write_lock:
                with (dirs[0] / "decisions.md").open("a") as f:
                    f.write(f"- {day} {key}: {choice} (matej, clicked)\n")
                commit(notes, f"{work}: {key} decided, {choice}")
            back = (
                urlsplit(self.headers.get("Referer", "")).path or f"/{quote(prefix)}/"
            )
            self.send_response(303)
            self.send_header("Location", back)
            self.end_headers()
            return None

        def translate_path(self, path: str) -> str:
            base = self.serve_from.resolve()
            target = (base / unquote(urlsplit(path).path).lstrip("/")).resolve()
            return str(target if target.is_relative_to(base) else base / "__outside__")

        def log_message(self, format: str, *args) -> None:
            pass

    server = http.server.ThreadingHTTPServer((host, port), Handler)
    print(f"serving notes from {', '.join(map(str, roots))} on http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def default_roots() -> list[Path]:
    env = os.environ.get("NOTES_ROOTS")
    if env:
        return [Path(p).expanduser() for p in env.split(os.pathsep) if p]
    return [Path.home() / "git"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p_next = sub.add_parser("next")
    p_next.add_argument("letter", choices=sorted(BUCKETS))
    p_new = sub.add_parser("new")
    p_new.add_argument("letter", choices=["d", "w"])
    p_new.add_argument("slug")
    p_new.add_argument("--html", action="store_true", help="a doc with a diagram")
    sub.add_parser("index")
    p_commit = sub.add_parser("commit")
    p_commit.add_argument("subject")
    sub.add_parser("status")
    p_file = sub.add_parser("file")
    p_file.add_argument("work")
    p_file.add_argument("part")
    p_file.add_argument(
        "transcript", help="the notification's output-file or the agent id"
    )
    p_file.add_argument("--checked", required=True, help="what the lead checked first")
    p_serve = sub.add_parser("serve")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--roots", nargs="*", type=Path)
    args = parser.parse_args()

    if args.cmd == "serve":
        serve(args.roots or default_roots(), args.host, args.port)
        return

    notes = project_root(args.root) / ".notes"
    if args.cmd == "init":
        init(notes)
        return
    if not notes.exists():
        sys.exit(f"{notes} does not exist, run init first")
    if args.cmd == "next":
        print(next_id(notes, args.letter))
    elif args.cmd == "new":
        new(notes, args.letter, args.slug, args.html)
    elif args.cmd == "index":
        write_index(notes)
        print(notes / "index.html")
    elif args.cmd == "commit":
        commit(notes, args.subject)
    elif args.cmd == "status":
        status(notes)
    elif args.cmd == "file":
        file_reply(notes, args.work, args.part, args.transcript, args.checked)


if __name__ == "__main__":
    main()
