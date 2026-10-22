#!/usr/bin/env python3
"""Inventory a code-and-data package without executing anything in it.

Usage:
    python3 <skill>/scripts/census.py <package_dir> --out ew/census

Writes two files into --out:
  census.json  one record per file (relative path, bytes, SHA-256, type by extension) plus a
               summary: counts and bytes by type, languages, candidate entry points, software
  CENSUS.md    the same for people: counts and total bytes by type, the 30 largest files,
               candidate entry points with the files they call, software found on this machine

What is read: every file, to hash it, and the text of code files (do, R, Rmd, py, jl, m, sas, sps)
and Makefiles, for the regex scans below. Nothing else is opened and nothing in the package is
run. .git is skipped; symbolic links are recorded with their target, not followed.

Candidate entry points: code files named master*, main*, run*, 0_*, 00_*; Makefiles; do-files with
`do` or `run` calls; R files that call source(); Python files with `if __name__`. The files they
call are listed as written in the code (macros and variables are not resolved).

Software: stata-mp, stata-se, stata, StataMP, StataSE on PATH, and /Applications/Stata*/ app
bundles (version from Contents/Info.plist; Stata is never launched); R, Rscript, python3, julia
(`--version`, run from a neutral directory); matlab (presence only). A program on PATH that lives
inside the package is recorded but never run.

Exit status: 0 on success; 2 if the package directory is missing or --out lies inside it.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TYPES = {".do": "do", ".ado": "ado", ".r": "R", ".rmd": "Rmd", ".py": "py", ".ipynb": "ipynb",
         ".jl": "jl", ".m": "m", ".sas": "sas", ".sps": "sps", ".dta": "dta", ".csv": "csv",
         ".xlsx": "xlsx", ".xls": "xls", ".parquet": "parquet", ".json": "json", ".txt": "txt",
         ".md": "md", ".pdf": "pdf", ".tex": "tex", ".log": "log"}
LANGUAGES = {"do": "Stata", "ado": "Stata", "R": "R", "Rmd": "R", "py": "Python",
             "ipynb": "Python", "jl": "Julia", "m": "MATLAB", "sas": "SAS", "sps": "SPSS"}
SCANNED = {"do", "R", "Rmd", "py", "jl", "m", "sas", "sps"}
MAX_SCAN = 10 * 1024 * 1024  # larger code files are hashed but not scanned
APPLICATIONS = "/Applications"
STATA_NAMES = ("stata-mp", "stata-se", "stata", "StataMP", "StataSE")

ENTRY_NAME_RE = re.compile(r"^(?:(?:master|main|run|runall)(?:[ ._-].*)?|0+_.*)$", re.IGNORECASE)
DO_CALL_RE = re.compile(r'^[ \t]*(?:(?:qui\w*|cap\w*|noi\w*)[ \t]*:?[ \t]+)*(?:do|run)[ \t]+'
                        r'(?:`"([^"\n]+)"\'|"([^"\n]+)"|([^\s,]+))', re.MULTILINE)
SOURCE_RE = re.compile(r'\b(?:sys\.)?source\s*\(\s*(?:file\s*=\s*)?(?:(["\'])(.+?)\1|([^)\n]*))')
MAIN_RE = re.compile(r"^[ \t]*if\s+__name__\s*==", re.MULTILINE)
CODE_EXT = r"(?:do|ado|R|r|Rmd|py|jl|m|sas|sps|ipynb)"
QUOTED_CODE_RE = re.compile(r'(["\'])([^"\'\n]+?\.' + CODE_EXT + r')\1')
MAKE_TOKEN_RE = re.compile(r'[^\s:;=\'"]+\.' + CODE_EXT + r'\b')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk(root: Path) -> list:
    """One record per file under root, sorted by path; .git skipped, links not followed."""
    records = []
    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for name in [d for d in dirnames if (base / d).is_symlink()] + sorted(filenames):
            path = base / name
            if name == ".git":
                continue
            rel = path.relative_to(root).as_posix()
            rec = {"path": rel, "bytes": None, "sha256": None,
                   "type": TYPES.get(path.suffix.lower(), "other")}
            if path.is_symlink():
                rec["symlink"] = os.readlink(path)
                if name in dirnames:
                    dirnames.remove(name)
            else:
                try:
                    rec["bytes"], rec["sha256"] = path.stat().st_size, sha256(path)
                except OSError as exc:
                    rec["error"] = exc.strerror or str(exc)
            records.append(rec)
    return sorted(records, key=lambda r: r["path"])


def calls_in(kind: str, text: str) -> list:
    """The files a script calls, as written, by cheap regex."""
    if kind == "do":
        found = [next(g for g in m.groups() if g).rstrip(",") for m in DO_CALL_RE.finditer(text)]
    elif kind in ("R", "Rmd"):
        found = []
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            for m in SOURCE_RE.finditer(line):
                found.append(m.group(2) if m.group(2) is not None else f"source({m.group(3).strip()})")
    elif kind == "make":
        found = MAKE_TOKEN_RE.findall(text)
    else:
        found = [m.group(2) for m in QUOTED_CODE_RE.finditer(text)]
    return list(dict.fromkeys(found))


def entry_point(rec: dict, root: Path):
    """Return {path, type, why, calls} if the file looks like an entry point, else None."""
    name = rec["path"].rsplit("/", 1)[-1]
    kind = rec["type"]
    is_make = name.lower() in ("makefile", "gnumakefile") or name.lower().endswith(".mk")
    why = ["named like an entry point"] if (kind in LANGUAGES and
                                             ENTRY_NAME_RE.match(name.rsplit(".", 1)[0])) else []
    calls: list = []
    if (kind in SCANNED or is_make) and rec["sha256"] and rec["bytes"] <= MAX_SCAN:
        try:
            text = (root / rec["path"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return {"path": rec["path"], "type": kind, "why": why, "calls": []} if why else None
        calls = calls_in("make" if is_make else kind, text)
        if is_make:
            why.append("Makefile")
        elif kind == "do" and calls:
            why.append("calls other do-files")
        elif kind in ("R", "Rmd") and calls:
            why.append("calls source()")
        elif kind == "py" and MAIN_RE.search(text):
            why.append("has if __name__ == '__main__'")
    return {"path": rec["path"], "type": kind, "why": why, "calls": calls} if why else None


def inside(path: str, root: str) -> bool:
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def plist_version(bundle: str):
    try:
        with open(os.path.join(bundle, "Contents", "Info.plist"), "rb") as fh:
            info = plistlib.load(fh)
    except Exception:  # missing, unreadable, or malformed: the version is simply unknown
        return None
    version = info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")
    return str(version) if version else None


def stata_bundles(applications: str = APPLICATIONS) -> list:
    patterns = (os.path.join(applications, "Stata*", "*.app"), os.path.join(applications, "Stata*.app"))
    bundles = sorted({b for p in patterns for b in glob.glob(p)
                      if os.path.basename(b).lower().startswith("stata")})
    return [{"name": os.path.basename(b)[:-4], "where": b, "version": plist_version(b),
             "how": "app bundle; version from Contents/Info.plist; not launched"} for b in bundles]


def find_software(package: str, applications: str = APPLICATIONS) -> list:
    found, seen = [], set()
    for name in STATA_NAMES:
        path = shutil.which(name)
        if not path or os.path.realpath(path) in seen:
            continue
        seen.add(os.path.realpath(path))
        bundle = re.match(r"^(.*?\.app)/Contents/MacOS/", os.path.realpath(path))
        found.append({"name": name, "where": path,
                      "version": plist_version(bundle.group(1)) if bundle else None,
                      "how": "on PATH; " + ("version from its app bundle's Info.plist" if bundle
                                            else "version not read") + "; not launched"})
    found += stata_bundles(applications)
    for name in ("R", "Rscript", "python3", "julia"):
        path = shutil.which(name)
        if not path:
            continue
        rec = {"name": name, "where": path, "version": None, "how": f"{name} --version"}
        if inside(path, package):
            rec["how"] = "inside the package; not run"
        else:
            try:
                out = subprocess.run([path, "--version"], stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     timeout=30, cwd=tempfile.gettempdir()).stdout
                lines = [ln.strip() for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()]
                rec["version"] = lines[0] if lines else None
            except (OSError, subprocess.SubprocessError) as exc:
                rec["how"] += f" failed: {exc}"
        found.append(rec)
    matlab = [shutil.which("matlab")] + sorted(glob.glob(os.path.join(applications, "MATLAB*.app")))
    found += [{"name": "matlab", "where": m, "version": None, "how": "presence only"} for m in matlab if m]
    return found


def human(n: float) -> str:
    for unit in ("bytes", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def md(text) -> str:
    return str(text).replace("|", "\\|")


def render(label: str, generated: str, records: list, summary: dict) -> str:
    s = summary
    out = ["# Package census", "",
           f"Package `{md(label)}`, inventoried {generated} by census.py. Nothing in the package was "
           "executed; `.git` was skipped; symbolic links were recorded, not followed.", "",
           f"Files: {s['file_count']:,}; total {human(s['total_bytes'])} ({s['total_bytes']:,} bytes).",
           f"Languages: {', '.join(s['languages']) or 'none detected'}.", "",
           "## Files by type", "", "| Type | Files | Bytes |", "|---|---:|---:|"]
    out += [f"| {t} | {v['files']:,} | {v['bytes']:,} |" for t, v in s["by_type"].items()]
    sized = sorted((r for r in records if r["bytes"] is not None), key=lambda r: (-r["bytes"], r["path"]))
    out += ["", "## The 30 largest files", "", "| Path | Type | Bytes |", "|---|---|---:|"]
    out += [f"| `{md(r['path'])}` | {r['type']} | {r['bytes']:,} |" for r in sized[:30]]
    out += ["", "## Candidate entry points", ""]
    if s["entry_points"]:
        out += ["| Path | Why | Calls (as written in the code) |", "|---|---|---|"]
        for ep in s["entry_points"]:
            calls = ", ".join(f"`{md(c)}`" for c in ep["calls"][:15])
            more = f" (+{len(ep['calls']) - 15} more)" if len(ep["calls"]) > 15 else ""
            out.append(f"| `{md(ep['path'])}` | {'; '.join(ep['why'])} | {calls or 'none found'}{more} |")
    else:
        out.append("none found")
    out += ["", "## Software on this machine", "", f"OS: {s['os']['platform']}", ""]
    if s["software"]:
        out += ["| Software | Where | Version | How |", "|---|---|---|---|"]
        out += [f"| {md(x['name'])} | `{md(x['where'])}` | {md(x['version'] or '—')} | {md(x['how'])} |"
                for x in s["software"]]
    out.append(f"\nNot found: {', '.join(s['software_not_found']) or 'none'}.")
    odd = [r for r in records if r["sha256"] is None]
    if odd:
        out += ["", "## Not hashed", ""]
        out += [f"- `{md(r['path'])}`: " + (f"symbolic link to `{md(r['symlink'])}`" if "symlink" in r
                                            else f"unreadable ({md(r.get('error'))})") for r in odd]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package_dir", help="the package copy to inventory")
    parser.add_argument("--out", required=True, help="output directory, normally ew/census")
    args = parser.parse_args(argv)
    root, out = Path(args.package_dir), Path(args.out)
    if not root.is_dir():
        print(f"census.py: error: {root} is not a directory", file=sys.stderr)
        return 2
    if inside(str(out), str(root)):
        print(f"census.py: error: --out {out} is inside the package; write the census outside it "
              "(normally ew/census)", file=sys.stderr)
        return 2
    generated = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    records = walk(root)
    entry_points = [ep for ep in (entry_point(r, root) for r in records) if ep]
    software = find_software(str(root))
    by_type: dict = {}
    for r in records:
        slot = by_type.setdefault(r["type"], {"files": 0, "bytes": 0})
        slot["files"] += 1
        slot["bytes"] += r["bytes"] or 0
    names = {x["name"].lower() for x in software}
    wanted = {"Stata": "stata", "R": "r", "python3": "python3", "julia": "julia", "matlab": "matlab"}
    summary = {
        "file_count": len(records), "total_bytes": sum(r["bytes"] or 0 for r in records),
        "by_type": dict(sorted(by_type.items())),
        "languages": sorted({LANGUAGES[t] for t in by_type if t in LANGUAGES}),
        "entry_points": entry_points, "software": software,
        "software_not_found": [k for k, v in wanted.items() if not any(n.startswith(v) for n in names)],
        "os": {"platform": platform.platform(), "system": platform.system(),
               "release": platform.release(), "machine": platform.machine()},
    }
    doc = {"package": args.package_dir, "generated": generated, "generator": "census.py (expert-witness)",
           "files": records, "summary": summary}
    out.mkdir(parents=True, exist_ok=True)
    (out / "census.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    (out / "CENSUS.md").write_text(render(args.package_dir, generated, records, summary), encoding="utf-8")
    languages = ", ".join(summary["languages"]) or "none"
    print(f"census.py: {len(records):,} files, {human(summary['total_bytes'])}; "
          f"{len(entry_points)} candidate entry points; languages: {languages}")
    print(f"census.py: wrote {out / 'census.json'} (SHA-256 {sha256(out / 'census.json')}) "
          f"and {out / 'CENSUS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
