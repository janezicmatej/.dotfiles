#!/usr/bin/env python3
"""mechanics for a project's .notes/ dir, see ~/.config/claude/rules/notes.md

usage:
  notes.py [--root DIR] init              create .notes/ with its git repo, if missing
  notes.py [--root DIR] next d|w|q        print the next free id of a bucket
  notes.py [--root DIR] index             regenerate index.html, notes.css, the markdown pages and
                                          the portable copies of other/out/ in _out/
  notes.py [--root DIR] commit SUBJECT    regenerate the index, commit every change in .notes/
  notes.py serve [--port 8765] [--roots DIR ...]
                                          every project's notes on one port; roots default to
                                          $NOTES_ROOTS, else ~/git

DIR is the project root, by default the git toplevel of the current dir, else the current dir
"""

import argparse
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

BUCKETS = {"d": "docs", "w": "work", "q": "questions"}
ID_RE = re.compile(r"^(docs|work|questions)/([dwq])(\d{3})-")
README = (
    "Local notes, never pushed. Layout and rules: ~/.config/claude/rules/notes.md\n"
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
    for d in ("docs", "work", "questions", "other/in", "other/out"):
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


# pages: index.html, notes.css, _pages/ and _out/ are generated, never committed

CSS = Path(__file__).with_name("notes.css")
GENERATED = ("/index.html", "/notes.css", "/_pages/", "/_out/")
PAGES = "_pages"
OUT = "_out"
CSS_LINK = re.compile(r'<link\b[^>]*href="[^"]*notes\.css"[^>]*>', re.IGNORECASE)
BACK_NAV = re.compile(r'\s*<nav class="back">.*?</nav>', re.DOTALL | re.IGNORECASE)
ID_TOKEN = re.compile(r"(?<![\w/.-])([dwq]\d{3})(?![\w/-])")


def ensure_gitignore(notes: Path) -> None:
    path = notes / ".gitignore"
    lines = path.read_text().splitlines() if path.exists() else []
    missing = [g for g in GENERATED if g not in lines]
    if missing:
        path.write_text("\n".join([*lines, *missing]) + "\n")


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
    title = re.sub(r"^[dwq]\d{3}\b\s*", "", m[1].strip())
    return title, body[: m.start()] + body[m.end() :]


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


class Site:
    """what exists in .notes/ and where each item's page is, relative to .notes/"""

    def __init__(self, notes: Path) -> None:
        self.notes = notes
        self.docs = self._docs()
        self.work = sorted(p for p in (notes / "work").glob("w[0-9]*") if p.is_dir())
        self.questions = sorted((notes / "questions").glob("q[0-9]*.md"))
        self.other = {
            sub: sorted(f for f in (notes / "other" / sub).rglob("*") if f.is_file())
            for sub in ("in", "out")
            if (notes / "other" / sub).exists()
        }
        self.urls: dict[str, str] = {}
        for d in self.docs:
            self.urls[d["id"]] = d["page"]
        for w in self.work:
            self.urls[w.name[:4]] = self.page_of(w / "brief.md")
        for q in self.questions:
            self.urls[q.name[:4]] = self.page_of(q)

    def _docs(self) -> list[dict]:
        out = []
        for p in sorted((self.notes / "docs").glob("d[0-9]*")):
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
                }
            )
        return out

    def page_of(self, src: Path) -> str:
        """where a markdown file's rendered page lives, relative to .notes/"""
        rel = src.relative_to(self.notes).with_suffix(".html")
        return f"{PAGES}/{rel.as_posix()}"

    def href(self, target: str, from_page: str) -> str:
        """a link from one page to another, both relative to .notes/"""
        base = Path(from_page).parent
        return quote(Path(*([".."] * len(base.parts)), target).as_posix())


def status_tag(status: str) -> str:
    e = html.escape
    if status.startswith("current"):
        return f'<span class="tag good" title="{e(status)}">current</span>'
    if status.startswith("partly stale"):
        return f'<span class="tag warn" title="{e(status)}">stale</span>'
    if m := re.match(r"superseded by (d\d{3})", status):
        return f'<span class="tag" title="{e(status)}">superseded by {m[1]}</span>'
    return '<span class="tag bad">no status line</span>'


def page(site: Site, path: str, title: str, body: str) -> str:
    css = site.href("notes.css", path)
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
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


def inline_plain(text: str, site: Site, at: str) -> str:
    links: list[str] = []

    def keep(s: str) -> str:
        links.append(s)
        return f"\x00{len(links) - 1}\x00"

    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: keep(f'<a href="{html.escape(m[2])}">{html.escape(m[1])}</a>'),
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
    item_id = next((p[:4] for p in src.parts if re.match(r"[dwq]\d{3}-", p)), "")
    eyebrow = " · ".join(x for x in (item_id, kind) if x)
    parts = [
        f'<nav class="back"><a href="{site.href("index.html", at)}">← notes</a></nav>',
        "<header>",
        f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else "",
        f"<h1>{e(title)}</h1>",
    ]
    if meta:
        dl = "".join(
            f"<div><dt>{e(k)}</dt><dd>{inline(v, site, at)}</dd></div>"
            for k, v in meta.items()
        )
        parts.append(f'<dl class="md-meta">{dl}</dl>')
    parts += ["</header>", markdown(body, site, at)]
    if kind == "work":
        files = []
        for f in sorted(src.parent.rglob("*")):
            if not f.is_file() or f == src:
                continue
            target = site.page_of(f) if f.suffix == ".md" else f.relative_to(site.notes)
            files.append(f'<a href="{site.href(str(target), at)}">{e(f.name)}</a>')
        if files:
            parts.append(f'<p class="files">files: {" · ".join(files)}</p>')
    out = site.notes / at
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(site, at, title, "\n".join(p for p in parts if p)))


def clear(d: Path) -> None:
    if d.exists():
        for f in sorted(d.rglob("*"), reverse=True):
            f.unlink() if f.is_file() else f.rmdir()


def write_portable(site: Site) -> None:
    """other/out/ as it leaves .notes/: css inlined, no back link to an index it won't have"""
    out = site.notes / OUT
    clear(out)
    src = site.notes / "other" / "out"
    style = f"<style>\n{CSS.read_text()}</style>"
    for f in site.other.get("out", []):
        target = out / f.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if f.suffix != ".html":
            target.write_bytes(f.read_bytes())
            continue
        # the nav goes before the css comes in: its header comment shows a nav too
        text = BACK_NAV.sub("", f.read_text(errors="replace"), count=1)
        target.write_text(CSS_LINK.sub(lambda _: style, text, count=1))


def write_index(notes: Path) -> None:
    ensure_gitignore(notes)
    (notes / "notes.css").write_text(CSS.read_text())
    site = Site(notes)

    clear(notes / PAGES)
    write_portable(site)
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

    def section(name: str, rows: list[str], empty: str, plain: bool = False) -> str:
        head = f'<h2>{name} <span class="count">{len(rows)}</span></h2>'
        if not rows:
            return f'{head}<p class="empty">{empty}</p>'
        cls = "rows plain" if plain else "rows"
        return f'{head}<ul class="{cls}">{"".join(rows)}</ul>'

    def row(item_id: str, href: str, title: str, meta: str = "", cls: str = "") -> str:
        return (
            f'<li><span class="id">{e(item_id)}</span>'
            f'<span class="title {cls}"><a href="{href}">{e(title)}</a></span>'
            f'<span class="meta">{meta}</span></li>'
        )

    docs = [
        row(
            d["id"],
            quote(d["page"]),
            d["title"],
            status_tag(d["status"]),
            "superseded" if d["status"].startswith("superseded") else "",
        )
        for d in site.docs
    ]
    work = []
    for w in site.work:
        brief = w / "brief.md"
        title = w.name[5:]
        if brief.exists():
            title, _ = split_title(frontmatter(brief.read_text())[1], title)
        work.append(row(w.name[:4], quote(site.urls[w.name[:4]]), title))
    questions = []
    for q in site.questions:
        meta, body = frontmatter(q.read_text(errors="replace"))
        title, _ = split_title(body, q.stem)
        created = e(meta.get("created", ""))
        questions.append(row(q.name[:4], quote(site.page_of(q)), title, created))

    other = []
    for sub, files in site.other.items():
        for f in files:
            target = site.page_of(f) if f.suffix == ".md" else f.relative_to(notes)
            portable = ""
            if sub == "out" and f.suffix == ".html":
                rel = f.relative_to(notes / "other" / "out").as_posix()
                portable = (
                    f' <a class="tag info" href="{quote(f"{OUT}/{rel}")}">to send</a>'
                )
            other.append(
                f'<li><span class="title"><a href="{quote(str(target))}">{e(f.name)}</a>'
                f' <span class="tag">{sub}</span>{portable}</span></li>'
            )

    project = notes.parent.name
    body = "\n".join(
        [
            # under serve this is the hub, under a plain http.server it is this index
            '<nav class="back"><a href="/">← all notes</a></nav>',
            '<header class="index-head">',
            f"<h1>{e(project)} notes</h1>",
            (
                f"<p>{len(site.docs)} docs · {len(site.work)} in flight · "
                f"{len(site.questions)} open questions · generated {date.today()}</p>"
            ),
            "</header>",
            '<div class="index">',
            section("Docs", docs, "no docs"),
            section("Work in flight", work, "nothing in flight"),
            section("Open questions", questions, "no open questions"),
            section("Other", other, "nothing here", plain=True) if other else "",
            "</div>",
        ]
    )
    (notes / "index.html").write_text(
        page(site, "index.html", f"{project} notes", body)
    )


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
        f"<title>{html.escape(title)}</title>\n"
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
        work = len([p for p in (notes / "work").glob("w[0-9]*") if p.is_dir()])
        docs = len(list((notes / "docs").glob("d[0-9]*")))
        last = git(notes, "log", "-1", "--format=%cs", check=False).strip()
        meta = f"{docs} docs · {work} in flight · {questions} open · {last or 'no commits'}"
        rows.append(
            f'<li data-name="{e(prefix.lower())}">'
            f'<span class="title"><a href="/{quote(prefix)}/">{e(prefix)}</a></span>'
            f'<span class="meta">{meta}</span></li>'
        )
    body = (
        '<header class="index-head"><h1>notes</h1>'
        f"<p>{len(projects)} projects · generated {date.today()}</p></header>"
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
        text = (notes / d["page"]).read_text(errors="replace")
        out.append((d["id"], d["title"], d["page"], page_text(text)))
    mds = [*site.questions, *(f for w in site.work for f in sorted(w.rglob("*.md")))]
    mds += [f for files in site.other.values() for f in files if f.suffix == ".md"]
    for f in mds:
        _, body = frontmatter(f.read_text(errors="replace"))
        title, _ = split_title(body, f.stem)
        item = next((p[:4] for p in f.parts if re.match(r"[dwq]\d{3}-", p)), "")
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


def serve(roots: list[Path], host: str, port: int) -> None:
    import http.server
    from urllib.parse import parse_qs, unquote, urlsplit

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
                return self.send_text(
                    hub(find_notes(roots)), "text/html; charset=utf-8"
                )
            if path == "/notes.css":
                return self.send_text(CSS.read_text(), "text/css; charset=utf-8")
            projects = find_notes(roots)
            prefix = max(
                (p for p in projects if path == f"/{p}" or path.startswith(f"/{p}/")),
                key=len,
                default=None,
            )
            if prefix is None:
                return self.send_error(404, "no such project")
            if path == f"/{prefix}":
                self.send_response(301)
                self.send_header("Location", f"/{quote(prefix)}/")
                self.end_headers()
                return None
            rest = path[len(prefix) + 2 :]
            notes = projects[prefix]
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
            self.serve_from = projects[prefix]
            self.path = "/" + rest
            return super().do_GET()

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
    import os

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
    sub.add_parser("index")
    p_commit = sub.add_parser("commit")
    p_commit.add_argument("subject")
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
    elif args.cmd == "index":
        write_index(notes)
        print(notes / "index.html")
    elif args.cmd == "commit":
        commit(notes, args.subject)


if __name__ == "__main__":
    main()
