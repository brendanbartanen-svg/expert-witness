#!/usr/bin/env python3
"""Scan files for things that must not leave the host's machine (references/disclosure.md).

Usage:
    python3 <skill>/scripts/disclosure_check.py <path>... [--min-cell 10]
        [--terms ew-local/sensitive-terms.txt] [--allow ew/disclosure/allow.txt]
        [--pre-report PRE-REPORT.md] [--quiet]

Paths are files or directories (scanned recursively). Skipped: anything under .git/ or ew-local/,
symbolic links, and binary files (a known binary extension such as .dta, .xlsx, .pdf, .png, or a
NUL byte in the first 8 KB). Every other file is read as text: md, csv, txt, log, py, R, do, json,
tex, and also .patch, .smcl and other text files, so that nothing committed escapes the scan.

Rules; each hit prints as  path:line: rule: excerpt
  email        an email address
  phone        a phone number: 3-3-4 digits with separators, optional +1 and parentheses
  long-id      a run of 7+ digits that is not part of a decimal number (no '.' before it, no '.'
               and digit after it, so 'record 90210537.' is a hit) and not part of a hexadecimal
               digest of 32+ characters (SHA-256, git object ids)
  course-code  \\b[A-Z]{3,4}\\s?\\d{3}[A-Z]?\\b, as in ECON 201
  term         a line of the sensitive-terms file: case-insensitive, whole word
  small-cell   n = 7 (an n or N set to an integer below --min-cell); and, in markdown tables (.md)
               and CSV/TSV files, an integer cell below --min-cell in a column whose header looks
               like a count: n, N, count(s), students, obs, observations, respondents, sections,
               instructors (an underscore counts as a word break, so n_treated qualifies)
  quote        a span inside straight or curly double quotes longer than 12 words
  listing      in .log files, 3+ consecutive lines that look like Stata `list` output (  1. ...)
               or an R data-frame print (1 value value): likely individual rows

Allow list: one 'rule:pattern|reason' per line (rule is one of the names above); it suppresses
hits of that rule only, whose excerpt contains the pattern (literal, case-sensitive). The older
'pattern|reason' form applies to every rule. Lines starting with # are comments; an entry without
a reason is ignored, with a warning. --terms and --allow default to the run directory's files and
may be absent.

--pre-report PATH: a quoted span (quote rule) that also appears verbatim in PATH, after collapsing
whitespace, is public text from the pre-report or the paper and is not a hit; any other quoted span
is still flagged.

Exit status: 1 if any hit is not allowed (or a file could not be read); 0 otherwise; 2 for usage
errors such as a path that does not exist.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import os
import re
import sys

RULES = ("email", "phone", "long-id", "course-code", "term", "small-cell", "quote", "listing")
SKIP_DIRS = {".git", "ew-local"}
BINARY_EXTS = {".dta", ".xlsx", ".xls", ".xlsm", ".parquet", ".feather", ".pdf", ".png", ".jpg",
               ".jpeg", ".gif", ".tif", ".tiff", ".zip", ".gz", ".bz2", ".xz", ".7z", ".rds",
               ".rdata", ".rda", ".sav", ".sas7bdat", ".pkl", ".pickle", ".npy", ".npz", ".h5",
               ".docx", ".pptx", ".gph", ".woff", ".ttf", ".exe", ".dll", ".so", ".dylib"}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\w.])(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]\d{4}(?![\w.])")
LONG_ID_RE = re.compile(r"(?<![\d.])\d{7,}(?!\d|\.\d)")
HEX_RE = re.compile(r"(?<![0-9A-Za-z])(?=[0-9]*[A-Fa-f])[0-9A-Fa-f]{32,}(?![0-9A-Za-z])")
COURSE_RE = re.compile(r"\b[A-Z]{3,4}\s?\d{3}[A-Z]?\b")
INLINE_N_RE = re.compile(r"\b[nN]\s*=\s*(\d{1,3}(?:,\d{3})+|\d+)(?![\d.,]\d)")
QUOTE_RE = re.compile(r'"([^"\n]*)"|“([^”\n]*)”')
COUNT_HEADER_RE = re.compile(r"^(n|count|counts|students|obs|observations|respondents|sections|"
                             r"instructors)\b", re.IGNORECASE)
INT_CELL_RE = re.compile(r"\d{1,3}(?:,\d{3})+|\d+")
MD_DELIM_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
STATA_ROW_RE = re.compile(r"^\s*\d+\.\s+\S")
R_ROW_RE = re.compile(r"^\s*\d+\s+\S+\s+\S+")

Hit = collections.namedtuple("Hit", "path line rule excerpt span", defaults=("",))


def excerpt(line: str, start: int = 0, end: int = 0, width: int = 200) -> str:
    """The stripped line, or a window around the match if the line is long."""
    text = line.strip()
    if len(text) <= width:
        return text
    lead = len(line) - len(line.lstrip())
    a, b = max(0, start - lead - 80), min(len(text), end - lead + 80)
    return ("…" if a else "") + text[a:b] + ("…" if b < len(text) else "")


def line_hits(path: str, n: int, line: str, terms: list, min_cell: int) -> list:
    hits = []

    def add(rule, m, span=""):
        hits.append(Hit(path, n, rule, excerpt(line, m.start(), m.end()), span))

    for m in EMAIL_RE.finditer(line):
        add("email", m)
    for m in PHONE_RE.finditer(line):
        add("phone", m)
    digests = [m.span() for m in HEX_RE.finditer(line)]
    for m in LONG_ID_RE.finditer(line):
        if not any(a <= m.start() and m.end() <= b for a, b in digests):
            add("long-id", m)
    for m in COURSE_RE.finditer(line):
        add("course-code", m)
    for _, pattern in terms:
        for m in pattern.finditer(line):
            add("term", m)
    for m in INLINE_N_RE.finditer(line):
        if int(m.group(1).replace(",", "")) < min_cell:
            add("small-cell", m)
    for m in QUOTE_RE.finditer(line):
        span = m.group(1) if m.group(1) is not None else m.group(2)
        if len(span.split()) > 12:
            add("quote", m, span)
    return hits


def count_columns(header: list) -> list:
    return [i for i, h in enumerate(header)
            if COUNT_HEADER_RE.match(h.strip(" *_`\t").replace("_", " "))]


def small_cells(path: str, n: int, row: list, header: list, cols: list, raw: str, min_cell: int) -> list:
    hits = []
    for i in cols:
        cell = row[i].strip(" *_`\t") if i < len(row) else ""
        if INT_CELL_RE.fullmatch(cell) and int(cell.replace(",", "")) < min_cell:
            hits.append(Hit(path, n, "small-cell", f"{excerpt(raw)}  [{header[i].strip()} = {cell}]"))
    return hits


def csv_hits(path: str, lines: list, delimiter: str, min_cell: int) -> list:
    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    hits: list = []
    try:
        header = next(reader, [])
        cols = count_columns(header)
        for row in reader if cols else ():
            n = reader.line_num
            hits += small_cells(path, n, row, header, cols, lines[n - 1], min_cell)
    except csv.Error:  # malformed CSV: the line rules above still applied
        pass
    return hits


def md_split(line: str) -> list:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def md_hits(path: str, lines: list, min_cell: int) -> list:
    hits, i = [], 0
    while i + 1 < len(lines):
        if "|" in lines[i] and "|" in lines[i + 1] and MD_DELIM_RE.match(lines[i + 1]):
            header = md_split(lines[i])
            cols, j = count_columns(header), i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                if cols:
                    hits += small_cells(path, j + 1, md_split(lines[j]), header, cols, lines[j], min_cell)
                j += 1
            i = j
        else:
            i += 1
    return hits


def listing_hits(path: str, lines: list) -> list:
    hits, run = [], 0
    for n, line in enumerate(lines + [""], 1):
        if STATA_ROW_RE.match(line) or R_ROW_RE.match(line):
            run += 1
            continue
        if run >= 3:
            first = n - run
            hits.append(Hit(path, first, "listing",
                            f"{excerpt(lines[first - 1])}  [{run} consecutive row-like lines]"))
        run = 0
    return hits


def scan_text(path: str, text: str, terms: list, min_cell: int) -> list:
    lines = text.splitlines()
    hits = []
    for n, line in enumerate(lines, 1):
        hits += line_hits(path, n, line, terms, min_cell)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv"):
        hits += csv_hits(path, lines, "\t" if ext == ".tsv" else ",", min_cell)
    elif ext in (".md", ".markdown"):
        hits += md_hits(path, lines, min_cell)
    elif ext == ".log":
        hits += listing_hits(path, lines)
    return sorted(hits, key=lambda h: (h.line, RULES.index(h.rule)))


def skip_reason(path: str):
    if set(os.path.normpath(path).split(os.sep)) & SKIP_DIRS:
        return "under .git/ or ew-local/"
    if os.path.islink(path):
        return "symbolic link"
    if not os.path.isfile(path):
        return "not a regular file"
    if os.path.splitext(path)[1].lower() in BINARY_EXTS:
        return "binary"
    with open(path, "rb") as fh:
        return "binary" if b"\0" in fh.read(8192) else None


def iter_files(paths: list):
    for p in paths:
        if os.path.isdir(p) and not os.path.islink(p):
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
                for name in sorted(filenames):
                    yield os.path.normpath(os.path.join(dirpath, name))
        else:
            yield os.path.normpath(p)


def load_terms(path: str):
    """[(term, compiled pattern)], or None if the file is absent."""
    if not path or not os.path.isfile(path):
        return None
    terms = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            term = line.strip()
            if term and not term.startswith("#"):
                words = r"\s+".join(re.escape(w) for w in term.split())
                terms.append((term, re.compile(r"(?<!\w)" + words + r"(?!\w)", re.IGNORECASE)))
    return terms


def load_allow(path: str) -> tuple:
    """([{rule, pattern, reason, line, used}], warnings); rule None = every rule; absent file = []."""
    entries, warnings = [], []
    if not path or not os.path.isfile(path):
        return entries, warnings
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            pattern, _, reason = line.rpartition("|")
            rule, colon, rest = pattern.partition(":")
            if colon and rule in RULES:
                pattern = rest
            else:
                if colon and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", rule):
                    warnings.append(f"{path}:{n}: '{rule}' is not a rule name ({', '.join(RULES)}); "
                                    "the entry is read as an unscoped pattern for every rule")
                rule = None
            if not pattern.strip() or not reason.strip():
                warnings.append(f"{path}:{n}: not 'rule:pattern|reason' with a pattern and a reason; "
                                "entry ignored")
                continue
            entries.append({"rule": rule, "pattern": pattern.strip(), "reason": reason.strip(),
                            "line": n, "used": 0})
    return entries, warnings


def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", metavar="path", help="files or directories to scan")
    parser.add_argument("--min-cell", type=positive_int, default=10, help="minimum cell count (10)")
    parser.add_argument("--terms", default="ew-local/sensitive-terms.txt", help="sensitive-terms file")
    parser.add_argument("--allow", default="ew/disclosure/allow.txt", help="allow list")
    parser.add_argument("--pre-report", help="quoted spans found in this file are not quote hits")
    parser.add_argument("--quiet", action="store_true", help="print only the summary")
    args = parser.parse_args(argv)
    missing = [p for p in args.paths if not os.path.lexists(p)]
    if missing:
        print(f"disclosure_check.py: error: no such file or directory: {', '.join(missing)}",
              file=sys.stderr)
        return 2
    terms = load_terms(args.terms)
    allow, warnings = load_allow(args.allow)
    for warning in warnings:
        print(f"disclosure_check.py: warning: {warning}", file=sys.stderr)
    public = None
    if args.pre_report and os.path.isfile(args.pre_report):
        with open(args.pre_report, encoding="utf-8", errors="replace") as fh:
            public = " ".join(fh.read().split())

    scanned, skipped, unreadable, open_hits, suppressed, exempted = 0, {}, [], [], 0, 0
    for path in iter_files(args.paths):
        try:
            reason = skip_reason(path)
            if reason is None:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
        except OSError as exc:
            unreadable.append(f"{path} ({exc.strerror})")
            continue
        if reason:
            skipped.setdefault(reason, []).append(path)
            continue
        scanned += 1
        for hit in scan_text(path, text, terms or [], args.min_cell):
            if public is not None and hit.rule == "quote" and " ".join(hit.span.split()) in public:
                exempted += 1
                continue
            entry = next((e for e in allow if e["rule"] in (None, hit.rule)
                          and e["pattern"] in hit.excerpt), None)
            if entry:
                entry["used"] += 1
                suppressed += 1
                continue
            open_hits.append(hit)
            if not args.quiet:
                print(f"{hit.path}:{hit.line}: {hit.rule}: {hit.excerpt}")

    summary = [f"disclosure_check: scanned {scanned} file(s); min cell {args.min_cell}"]
    for reason, paths in skipped.items():
        listed = "" if args.quiet else ": " + ", ".join(paths[:20]) + (" …" if len(paths) > 20 else "")
        summary.append(f"  not scanned ({reason}): {len(paths)}{listed}")
    summary += [f"  could not read: {p}" for p in unreadable]
    summary.append(f"  terms: {len(terms)} from {args.terms}" if terms is not None
                   else f"  terms: rule skipped, {args.terms} not found")
    summary.append(f"  allow: {len(allow)} entries from {args.allow}; {suppressed} hit(s) suppressed"
                   if os.path.isfile(args.allow) else f"  allow: none ({args.allow} not found)")
    if not args.pre_report:
        summary.append("  pre-report: not given; no quoted span is exempted")
    else:
        summary.append(f"  pre-report: {exempted} quoted span(s) found in {args.pre_report}, exempted"
                       if public is not None else f"  pre-report: {args.pre_report} not found; "
                       "no quoted span is exempted")
    if not args.quiet:
        summary += [f"  allow entry unused (line {e['line']}): "
                    f"{e['rule'] + ':' if e['rule'] else ''}{e['pattern']}" for e in allow if not e["used"]]
    counts = collections.Counter(h.rule for h in open_hits)
    summary.append("  hits not allowed: " + ", ".join(f"{r} {counts[r]}" for r in RULES))
    failed = bool(open_hits or unreadable)
    summary.append(f"  result: FAIL, {len(open_hits)} hit(s) not allowed"
                   + (f", {len(unreadable)} file(s) unreadable" if unreadable else "")
                   if failed else "  result: PASS")
    print("\n".join(summary))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
