#!/usr/bin/env python3
"""Create the REPORT.md skeleton, the ew/ tree, ew-local/ and .gitignore entries from a pre-report.

Usage, from the run directory (the git checkout the witness works in):

    python3 <skill>/scripts/init_report.py PRE-REPORT.md [--report REPORT.md] [--host HOST.md] [--force]

Every output path is relative to the current directory, which is taken to be the run directory.

Parsing. The title comes from the '# Pre-report: {title}' heading. Each item is a heading
'### {ID} — {title}' (ID A1…, B1…, C1…; an em dash or a plain hyphen between ID and title) with
the bold fields **Tier:**, **Question:**, **Paper's statement at issue:**, **Specification:**,
**Output:**, **Disclosure:**, **Resolution:**, **Exhibits:**, **Cells:**, **Notes:**. A field starts
at its label at the start of a line and runs to the next field label or heading; it may span lines
and contain lists. Fenced code blocks are not searched for headings or labels. An item runs to the
next heading of level 1-3.

Outputs.
  REPORT.md   references/report-template.md with one section per item: the title in each heading,
              Tier in the summary table, and (Parts B and C) the Question copied verbatim into the
              blockquote; every other field is a {…} placeholder. Refused if it exists, unless --force.
  ew/         INTAKE.md, STEPLOG.md, INTERVENTIONS.md, census/, log/, reproduction/reported.csv,
              items/<ID>/ for every item, disclosure/allow.txt (texts in scripts/templates/);
              .gitkeep in otherwise empty directories. Existing files are never overwritten;
              STEPLOG.md gets a new timestamped line on every run.
  ew-local/   created; never committed.
  .gitignore  gains ew-local/ and the package directory from HOST.md's **Package directory:** field
              (a loud warning if HOST.md or the field is missing).

Exit status: 0 on success; 1 if the pre-report cannot be used (no '# Pre-report:' heading, no items,
malformed item headings, duplicate IDs) or REPORT.md exists without --force; 2 for usage errors.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "PRE-REPORT-TEMPLATE.md"
TEMPLATES = Path(__file__).resolve().parent / "templates"  # texts of the ew/ files
PARTS = (("A", "Part A — Reproduction"), ("B", "Part B — Requested analyses"),
         ("C", "Part C — Documentation"))
FIELD_NAMES = ("Tier", "Question", "Paper's statement at issue", "Specification", "Output",
               "Disclosure", "Resolution", "Exhibits", "Cells", "Notes")
EXPECTED = {"A": ("Tier", "Exhibits", "Cells", "Notes"),
            "B": ("Tier", "Question", "Paper's statement at issue", "Specification", "Output",
                  "Disclosure", "Resolution"),
            "C": ("Tier", "Question", "Specification", "Output")}

HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*$")
TITLE_RE = re.compile(r"^Pre-report:[ \t]*(.*)$", re.IGNORECASE)
ITEM_RE = re.compile(r"^([ABC]\d+)[ \t]+(?:—|-)[ \t]+(\S.*)$")
IDLIKE_RE = re.compile(r"^[*_`]*([A-Za-z]\d+)(.*)$")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")
FIELD_RE = re.compile(r"^[ \t]*(?:[-*+][ \t]+)?\*\*(Tier|Question|Paper['’]s statement at issue"
                      r"|Specification|Output|Disclosure|Resolution|Exhibits|Cells|Notes):\*\*[ \t]*(.*)$",
                      re.IGNORECASE)
PKG_RE = re.compile(r"\*\*Package directory:\*\*[ \t]*(.*)$", re.IGNORECASE)

HEADER = """\
**Status:** {COMPLETE | PARTIAL (outstanding: …) | STOPPED BY HOST (phase …, item …)}

**Pre-report:** PRE-REPORT.md @ {commit} (blob {hash})

**Host declaration:** HOST.md @ {commit} (blob {hash})

**Model:** {actual model id} (requested: {model}); effort: {actual} (requested: {effort})

**Run:** {start} – {end}; phases: census {m}m, read {m}m, reproduce {m}m, items {m}m, review {m}m

**Package:** {dir}; {N} files; census {hash of census.json}

**Disclosure terms in force:** min cell {n}; section rows {permitted under random labels | not permitted}; {other}"""
A_FIELDS = """\
**Exhibits:** {tables/figures}

**Source:** {script → output file}, run from {raw | intermediate file `…`}

**Finding:** {REPRODUCED | REPRODUCED-WITHIN-TOLERANCE | DIFFERS | COULD-NOT-RUN | NOT-APPLICABLE}

**Comparison:** ew/reproduction/COMPARE.md#{anchor}; {k} of {n} cells within tolerance; largest difference {…} at {cell}

**Observations:** {anything encountered that bears on this exhibit: exclusions not described, constructions that differ from the text, hand steps} | none

**Files:** ew/log/{…}"""
B_FIELDS = """\
**Specification followed:** {the literal reading; alternative reading, if reported}

**What was done:** {script path; inputs with hashes; definitions used; seeds; software}

**Result:**

{table or numbers, disclosure applied}

**Finding:** {ANSWERED | ANSWERED-WITH-RESTRICTIONS | NOT-ANSWERABLE | NOT-ATTEMPTED}

**Plain result:** {one sentence, true whichever way the parties hoped it would come out}

**Bearing on the paper's statement:** The pre-report cites: "{quoted sentence}" (p. {n}). The requested quantity {is | is not} consistent with it in the following sense: {…}.

**Observations:** {…} | none

**Disclosure notes:** {suppressions applied; rule numbers} | none

**Files:** ew/items/@ID@/{script}, ew/items/@ID@/{log}, ew/items/@ID@/{outputs}"""
C_FIELDS = """\
**Answer:** {description, with file and line references into the package}

**Finding:** {ANSWERED | ANSWERED-WITH-RESTRICTIONS | NOT-ANSWERABLE | NOT-ATTEMPTED}

**Files:** {…}"""
TAIL = """\
## Noted, outside scope

- {one line each; no numbers; no conclusions} | none

## Interventions

{count} recorded; full log in ew/INTERVENTIONS.md. {one line each: timestamp, kind, followed/declined}

## Environment

{from CENSUS.md: OS, software and versions, packages installed during the run and by whose permission}

## Method notes

{anything general: how control-SD units were computed; the RI procedure and the number of assignments enumerated; clustering; the tolerance rule; the labeling scheme}
"""


class PreReportError(Exception):
    """The pre-report cannot be parsed into items."""


def canonical(label: str) -> str:
    key = label.replace("’", "'").lower()
    return next(name for name in FIELD_NAMES if name.lower() == key)


def heading_problem(level: int, text: str) -> str:
    """Say why a heading that starts like an item ID is not an item heading."""
    if level != 3:
        return f"item headings are level 3 ('### '), not '{'#' * level} '"
    ident, rest = IDLIKE_RE.match(text).groups()
    if text[0] in "*_`":
        return "the ID must not be wrapped in emphasis or code marks"
    if not re.fullmatch(r"[ABC]\d+", ident):
        return f"'{ident}' is not an item ID (items are A1…, B1…, C1…, capital letter)"
    if re.match(r"[ \t]+–", rest):
        return "use an em dash '—' or a hyphen '-' after the ID, not an en dash '–'"
    if not re.match(r"[ \t]+(?:—|-)", rest):
        return "the ID must be followed by ' — ' (or ' - ') and the title"
    return "the title after the dash is missing"


def parse_prereport(text: str) -> tuple[str, list[dict]]:
    """Return (title, items); each item is {'id', 'title', 'line', 'fields': {name: text}}."""
    title, items, problems = None, [], []
    item = field = None
    fence_line = 0
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fence_line = 0 if fence_line else n
        elif not fence_line:
            heading = HEADING_RE.match(line)
            if heading:
                level, body = len(heading.group(1)), heading.group(2)
                field = None
                found = TITLE_RE.match(body) if level == 1 else None
                if found and title is None:
                    title = found.group(1).strip()
                found = ITEM_RE.match(body) if level == 3 else None
                if found:
                    item = {"id": found.group(1), "title": found.group(2).strip(), "line": n,
                            "fields": {}}
                    items.append(item)
                    continue
                if IDLIKE_RE.match(body):
                    problems.append(f"  line {n}: {line.strip()}\n      {heading_problem(level, body)}")
                if level <= 3:
                    item = None
                continue
            label = FIELD_RE.match(line) if item is not None else None
            if label:
                field = canonical(label.group(1))
                item["fields"].setdefault(field, []).append(label.group(2))
                continue
        if item is not None and field is not None:
            item["fields"][field].append(line)
    if fence_line:
        problems.append(f"  line {fence_line}: a fenced code block is never closed; "
                        "headings after it cannot be read")
    if title is None:
        problems.insert(0, "  no '# Pre-report: {title}' heading")
    elif not title:
        problems.insert(0, "  the '# Pre-report:' heading has no title")
    first_seen: dict = {}
    for it in items:
        if it["id"] in first_seen:
            problems.append(f"  line {it['line']}: item {it['id']} already appears at line "
                            f"{first_seen[it['id']]}")
        first_seen.setdefault(it["id"], it["line"])
    if not items and not problems:
        problems.append("  no items found: no heading of the form '### A1 — {title}'")
    if problems:
        raise PreReportError("\n".join(problems))
    for it in items:
        it["fields"] = {name: "\n".join(lines).strip() for name, lines in it["fields"].items()}
    return title, items


def table_cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def blockquote(text: str) -> list[str]:
    return [f"> {line}" if line.strip() else ">" for line in text.split("\n")]


def render_report(title: str, items: list[dict]) -> str:
    out = [f"# Expert Witness Report: {title}", "", HEADER, "", "## Summary of findings", "",
           "| Item | Tier | Finding | Result in one line |", "|---|---|---|---|"]
    ordered = [it for part, _ in PARTS for it in items if it["id"][0] == part]
    for it in ordered:
        tier = it["fields"].get("Tier")
        out.append(f"| {it['id']} | {table_cell(tier) if tier else '—'} | {{…}} | {{…}} |")
    for part, heading in PARTS:
        out += ["", f"## {heading}"]
        members = [it for it in ordered if it["id"][0] == part]
        if not members:
            out += ["", "none"]
        for it in members:
            out += ["", f"### {it['id']} — {it['title']}", ""]
            if part == "A":
                out.append(A_FIELDS)
                continue
            label = ("**Question (from the pre-report, verbatim):**" if part == "B"
                     else "**Question (verbatim):**")
            question = (it["fields"].get("Question")
                        or "{the pre-report gives no **Question:** for this item}")
            fields = B_FIELDS if part == "B" else C_FIELDS
            out += [label, *blockquote(question), "", fields.replace("@ID@", it["id"])]
    return "\n".join(out + ["", TAIL])


def package_dir_from_host(host_path, root=".") -> tuple:
    """Return (package dir relative to root, None) or (None, why it could not be read)."""
    host = Path(host_path)
    if not host.is_file():
        return None, f"{host_path} not found"
    lines = host.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    for i, line in enumerate(lines):
        found = PKG_RE.search(line)
        if not found:
            continue
        value = found.group(1).strip() or (lines[i + 1].strip() if i + 1 < len(lines) else "")
        if not value or value.startswith("{"):
            return None, f"the **Package directory:** field in {host_path} is empty or still the placeholder"
        quoted = re.match(r"`([^`]+)`", value)
        raw = (quoted.group(1) if quoted else value.split()[0]).strip("'\"").rstrip(",;")
        path = Path(raw).expanduser()
        if path.is_absolute():
            try:
                path = path.resolve().relative_to(Path(root).resolve())
            except ValueError:
                return None, f"the package directory {raw} is outside the run directory"
        rel = Path(os.path.normpath(str(path))).as_posix()
        if rel in ("", ".", "..") or rel.startswith("../"):
            return None, f"the package directory {raw!r} is not a subdirectory of the run directory"
        return rel, None
    return None, f"{host_path} has no **Package directory:** field"


def now() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def write_new(path: Path, content: str, created: list) -> None:
    """Write a file only if it does not exist yet."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path.as_posix())


def build_tree(title: str, items: list[dict], message: str) -> list:
    created: list = []
    ew = Path("ew")
    write_new(ew / "INTAKE.md", template("INTAKE.md").replace("@TITLE@", title), created)
    write_new(ew / "INTERVENTIONS.md", template("INTERVENTIONS.md"), created)
    write_new(ew / "census" / ".gitkeep", "", created)
    write_new(ew / "log" / ".gitkeep", "", created)
    write_new(ew / "reproduction" / "reported.csv",
              "table,panel,row,column,quantity,value,digits,stars\n", created)
    for it in items:
        write_new(ew / "items" / it["id"] / ".gitkeep", "", created)
    write_new(ew / "disclosure" / "allow.txt", template("allow.txt"), created)
    steplog = ew / "STEPLOG.md"
    write_new(steplog, template("STEPLOG.md"), created)
    with steplog.open("a", encoding="utf-8") as fh:
        fh.write(f"- {now()} {message}\n")
    Path("ew-local").mkdir(exist_ok=True)
    return created


def ensure_gitignore(entries: list) -> list:
    """Append the entries .gitignore lacks; return the ones added."""
    def norm(line: str) -> str:
        line = line.strip()
        for suffix in ("/**", "/*", "/"):
            if line.endswith(suffix):
                line = line[: -len(suffix)]
                break
        return line.lstrip("/")

    path = Path(".gitignore")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    present = {norm(ln) for ln in text.splitlines() if ln.strip() and ln.lstrip()[0] not in "#!"}
    missing = [e for e in entries if norm(e) not in present]
    if missing:
        if text and not text.endswith("\n"):
            text += "\n"
        text += ("\n" if text else "") + "# expert-witness (init_report.py): never committed\n"
        path.write_text(text + "".join(e + "\n" for e in missing), encoding="utf-8")
    return missing


def loud(*lines: str) -> None:
    bar = "!" * 76
    print("\n".join([bar, "WARNING: " + lines[0], *lines[1:], bar]), file=sys.stderr)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("prereport", help="the pre-report, normally PRE-REPORT.md")
    parser.add_argument("--report", default="REPORT.md", help="report to create (default REPORT.md)")
    parser.add_argument("--host", default="HOST.md", help="host declaration (default HOST.md)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing report")
    args = parser.parse_args(argv)

    source = Path(args.prereport)
    if not source.is_file():
        print(f"init_report.py: error: {source} not found", file=sys.stderr)
        return 2
    try:
        title, items = parse_prereport(source.read_text(encoding="utf-8-sig"))
    except (PreReportError, UnicodeDecodeError) as exc:
        print(f"init_report.py: {source} cannot be used:\n{exc}\n"
              "Items must be headings of the form '### {ID} — {title}' (IDs A1…, B1…, C1…), with the "
              f"bold field labels written as in the template:\n  {TEMPLATE}", file=sys.stderr)
        return 1
    report = Path(args.report)
    if report.exists() and not args.force:
        print(f"init_report.py: {report} already exists; refusing to overwrite it "
              "(use --force to regenerate the skeleton)", file=sys.stderr)
        return 1
    for it in items:
        for name in EXPECTED[it["id"][0]]:
            if not it["fields"].get(name):
                print(f"init_report.py: warning: {it['id']} (line {it['line']}) has no **{name}:** field",
                      file=sys.stderr)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(title, items), encoding="utf-8")
    ids = ", ".join(it["id"] for it in items)
    created = build_tree(title, items, f"init_report.py run: {report} skeleton for {len(items)} "
                         f"items ({ids}){' (--force)' if args.force else ''}; ew/ tree checked")
    package, problem = package_dir_from_host(args.host)
    added = ensure_gitignore(["ew-local/"] + ([package + "/"] if package else []))
    print(f"init_report.py: wrote {report}: {len(items)} items ({ids})")
    print(f"init_report.py: created {len(created)} files under ew/; ew/STEPLOG.md updated; ew-local/ ready")
    print(f"init_report.py: .gitignore: {'added ' + ', '.join(added) if added else 'already complete'}")
    if problem:
        loud(f"{problem}.",
             "The package directory is NOT in .gitignore. The package holds the data and must never",
             "be committed: fix HOST.md and re-run init_report.py, or add the directory to .gitignore.",
             "The pre-commit hook also reads HOST.md and cannot guard the package until this is fixed.")
    elif not Path(package).is_dir():
        loud(f"the package directory {package}/ read from HOST.md does not exist.",
             f"{package}/ was added to .gitignore, but if HOST.md was misread the real package is not",
             "guarded: check the **Package directory:** field and .gitignore before the first commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
