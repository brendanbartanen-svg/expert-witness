#!/usr/bin/env python3
"""Compare the paper's printed cells with the reproduced values, cell by cell.

Usage:
    python3 <skill>/scripts/compare.py reported.csv reproduced.csv [--out COMPARE.md]

Both CSVs have the columns table,panel,row,column,quantity,value,digits,stars (header names are
matched case-insensitively). reported.csv transcribes the paper: value exactly as printed, digits =
the decimals printed, stars as printed. reproduced.csv holds the pipeline's values at full precision;
its digits and stars columns are optional. Rows are matched on table, panel, row, column, quantity.

Each reported cell gets one status. The reproduced value is rounded half-up to the cell's digits:
  MATCH                  the rounded value equals the printed value
  WITHIN-ONE-UNIT        it differs by exactly one unit in the last printed digit
  DIFFERS                it differs by more
  MISSING-IN-REPRODUCED  no reproduced row has the same keys
  NOT-NUMERIC            either value is not a number (a printed '<0.001', a blank); not compared
Counts (quantity n) have no rounding: MATCH only if the reproduced value equals the printed count
exactly, otherwise DIFFERS (a count off by one is never WITHIN-ONE-UNIT). Reproduced rows with no
reported counterpart are EXTRA. If both files have a stars column, stars are compared as printed
and a mismatch adds the secondary flag STARS-DIFFER. A printed value may carry parentheses or
brackets (standard errors), thousands separators, or a Unicode minus sign. A blank digits cell is
read from the printed value, and the cell's flags say so.

Output: COMPARE.md (default: beside reported.csv) with a summary per table (counts by status, cells
within tolerance, the largest absolute and relative differences, computed from the unrounded
reproduced value, with their cells) and a table of every cell. The summary is also printed.

Exit status: 0 whatever the comparison shows (it is information, not a gate); 2 if an input cannot
be read, lacks a required column, or repeats a key.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, getcontext
from pathlib import Path

getcontext().prec = 60
KEYS = ("table", "panel", "row", "column", "quantity")
STATUSES = ("MATCH", "WITHIN-ONE-UNIT", "DIFFERS", "MISSING-IN-REPRODUCED", "NOT-NUMERIC", "EXTRA")
THOUSANDS_RE = re.compile(r"^-?[1-9]\d{0,2}(?:,\d{3})+(?:\.\d*)?$")


class InputError(Exception):
    """An input file cannot be used."""


def parse_number(text: str):
    """The printed or reproduced value as a Decimal, or None if it is not a number."""
    s = text.strip().replace("−", "-")
    if len(s) >= 2 and (s[0], s[-1]) in (("(", ")"), ("[", "]")):
        s = s[1:-1].strip()
    if THOUSANDS_RE.match(s):
        s = s.replace(",", "")
    try:
        value = Decimal(s)
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def decimals_shown(value: Decimal) -> int:
    exponent = value.as_tuple().exponent
    return -exponent if exponent < 0 else 0


def classify(printed: Decimal, digits: int, reproduced: Decimal, count: bool = False) -> tuple:
    """(status, rounded) for one numeric cell; a count must equal the printed value exactly."""
    unit = Decimal(1).scaleb(-digits)
    rounded = reproduced.quantize(unit, rounding=ROUND_HALF_UP)
    if count:
        return ("MATCH" if reproduced == printed else "DIFFERS"), rounded
    gap = abs(rounded - printed)
    return ("MATCH" if gap == 0 else "WITHIN-ONE-UNIT" if gap == unit else "DIFFERS"), rounded


def read_cells(path: Path, required: tuple) -> tuple:
    """({key: row}, has_stars_column) in file order."""
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc.strerror}") from None
    with fh:
        reader = csv.reader(fh)
        header = [h.strip().lower() for h in next(reader, [])]
        missing = [c for c in required if c not in header]
        if missing:
            raise InputError(f"{path} lacks the column(s) {', '.join(missing)} "
                             "(expected table,panel,row,column,quantity,value,digits,stars)")
        cells: dict = {}
        for raw in reader:
            if not any(v.strip() for v in raw):
                continue
            row = {name: (raw[i].strip() if i < len(raw) else "") for i, name in enumerate(header)}
            row["_line"] = reader.line_num
            key = tuple(row[k] for k in KEYS)
            if key in cells:
                raise InputError(f"{path}: line {row['_line']} repeats the key of line "
                                 f"{cells[key]['_line']} ({' / '.join(key)})")
            cells[key] = row
    return cells, "stars" in header


def compare(reported: dict, reproduced: dict, stars: bool) -> list:
    """One result per reported cell, in order, then one per EXTRA reproduced cell."""
    results = []
    for key, rep in reported.items():
        pro = reproduced.get(key)
        res = {"key": key, "printed": rep["value"], "digits": rep["digits"],
               "reproduced": pro["value"] if pro else "", "rounded": "", "flags": [],
               "abs": None, "rel": None}
        printed = parse_number(rep["value"])
        digits = int(rep["digits"]) if rep["digits"].isdigit() else None
        if digits is None and printed is not None:
            digits = decimals_shown(printed)
            res["flags"].append(f"digits read from the printed value ({digits})")
        value = parse_number(pro["value"]) if pro else None
        if pro is None:
            res["status"] = "MISSING-IN-REPRODUCED"
        elif printed is None or value is None or digits is None:
            res["status"] = "NOT-NUMERIC"
        else:
            res["status"], rounded = classify(printed, digits, value, count=key[4].lower() == "n")
            res["rounded"] = format(rounded, "f")
            res["abs"] = abs(value - printed)
            res["rel"] = res["abs"] / abs(printed) if printed else None
            if rep["digits"].isdigit() and decimals_shown(printed) != digits:
                res["flags"].append(f"printed value shows {decimals_shown(printed)} decimals")
        if pro is not None and stars and rep.get("stars", "") != pro.get("stars", ""):
            res["flags"].append("STARS-DIFFER")
        results.append(res)
    for key, pro in reproduced.items():
        if key not in reported:
            results.append({"key": key, "printed": "", "digits": pro.get("digits", ""),
                            "reproduced": pro["value"], "rounded": "", "status": "EXTRA",
                            "flags": [], "abs": None, "rel": None})
    return results


def summarize(rows: list) -> dict:
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    numeric = [r for r in rows if r["abs"] is not None]
    relative = [r for r in numeric if r["rel"] is not None]
    return {"counts": counts, "stars": sum("STARS-DIFFER" in r["flags"] for r in rows),
            "reported": len(rows) - counts["EXTRA"],
            "within": counts["MATCH"] + counts["WITHIN-ONE-UNIT"],
            "max_abs": max(numeric, key=lambda r: r["abs"], default=None),
            "max_rel": max(relative, key=lambda r: r["rel"], default=None)}


def cell_label(key: tuple) -> str:
    return " / ".join(k or "—" for k in key[1:])


def describe(r, kind: str) -> str:
    if r is None:
        return "none (no numeric cells compared)"
    amount = (format(r["abs"].normalize(), "f") if kind == "abs"
              else "<0.01%" if r["rel"] * 100 < Decimal("0.01") else f"{float(r['rel']) * 100:.2f}%")
    return f"{amount} at {cell_label(r['key'])} (printed {r['printed']}, reproduced {r['reproduced']})"


def by_table(results: list) -> dict:
    tables: dict = {}
    for r in results:
        tables.setdefault(r["key"][0], []).append(r)
    return tables


def counts_line(s: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in s["counts"].items()) + f"; STARS-DIFFER {s['stars']}"


def md(text: str) -> str:
    return str(text).replace("|", "\\|")


def render(results: list, reported: Path, reproduced: Path) -> str:
    def digest(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    out = ["# Reproduction comparison", "",
           f"Printed cells: `{reported}` (SHA-256 {digest(reported)}).",
           f"Reproduced values: `{reproduced}` (SHA-256 {digest(reproduced)}).",
           f"Generated {datetime.datetime.now().astimezone().isoformat(timespec='seconds')} by compare.py.",
           "", "Rule: each reproduced value is rounded half-up to the printed digits of its cell; MATCH "
           "if it then equals the printed value, WITHIN-ONE-UNIT if it differs by exactly one unit in the "
           "last printed digit, DIFFERS otherwise. Counts (quantity n) must match exactly. Largest "
           "differences use the unrounded reproduced value.",
           "", "## Summary by table"]
    for table, rows in by_table(results).items():
        s = summarize(rows)
        out += ["", f"### {md(table) or '(no table label)'}", "",
                f"- {s['within']} of {s['reported']} cells within tolerance",
                f"- {counts_line(s)}",
                f"- Largest absolute difference: {md(describe(s['max_abs'], 'abs'))}",
                f"- Largest relative difference: {md(describe(s['max_rel'], 'rel'))}"]
    out += ["", "## All cells", "",
            "| Table | Panel | Row | Column | Quantity | Printed | Digits | Reproduced | Rounded "
            "| Status | Flags |",
            "|---|---|---|---|---|---:|---:|---:|---:|---|---|"]
    for r in results:
        cells = (*r["key"], r["printed"], r["digits"], r["reproduced"], r["rounded"], r["status"],
                 "; ".join(r["flags"]))
        out.append("| " + " | ".join(md(c) for c in cells) + " |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("reported", help="the paper's cells, normally ew/reproduction/reported.csv")
    parser.add_argument("reproduced", help="the pipeline's values, normally ew/reproduction/reproduced.csv")
    parser.add_argument("--out", help="report to write (default: COMPARE.md beside reported.csv)")
    args = parser.parse_args(argv)
    reported_path, reproduced_path = Path(args.reported), Path(args.reproduced)
    try:
        reported, stars_rep = read_cells(reported_path, KEYS + ("value", "digits"))
        reproduced, stars_pro = read_cells(reproduced_path, KEYS + ("value",))
    except InputError as exc:
        print(f"compare.py: error: {exc}", file=sys.stderr)
        return 2
    for rows in (reported, reproduced):
        for row in rows.values():
            row.setdefault("digits", "")
    results = compare(reported, reproduced, stars_rep and stars_pro)
    out = Path(args.out) if args.out else reported_path.with_name("COMPARE.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(results, reported_path, reproduced_path), encoding="utf-8")
    for table, rows in by_table(results).items():
        s = summarize(rows)
        print(f"{table or '(no table label)'}: {s['within']} of {s['reported']} cells within tolerance "
              f"({counts_line(s)})")
    print(f"compare.py: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
