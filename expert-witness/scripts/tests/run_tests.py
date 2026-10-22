#!/usr/bin/env python3
"""Tests for the expert-witness helper scripts, standard library only.

Run:   python3 scripts/tests/run_tests.py [-v] [unittest options, e.g. -k census]

Each test works in its own temporary directory; nothing under scripts/tests/fixtures/ is modified.
The install_hooks.sh tests need git and bash, and run git with the user's global and system
configuration switched off.
"""
from __future__ import annotations

import hashlib
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent
SKILL = SCRIPTS.parent
FIXTURES = TESTS / "fixtures"
DISC = FIXTURES / "disclosure"
sys.dont_write_bytecode = True  # keep __pycache__ out of the skill folder
sys.path.insert(0, str(SCRIPTS))

import census  # noqa: E402
import compare  # noqa: E402
import init_report  # noqa: E402

HIT_RE = re.compile(r"^(.+?):(\d+): ([a-z-]+): (.*)$")


def run(script, *args, cwd=None, env=None):
    """Run one of the scripts with this interpreter."""
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          cwd=cwd, env=env, capture_output=True, text=True)


def hits_of(result) -> set:
    """{(file name, line, rule)} from the checker's output."""
    found = set()
    for line in result.stdout.splitlines():
        m = HIT_RE.match(line)
        if m:
            found.add((Path(m.group(1)).name, int(m.group(2)), m.group(3)))
    return found


class TempDir(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ew-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def write(self, rel, text, base=None) -> Path:
        path = (base or self.tmp) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class HelpTests(unittest.TestCase):
    def test_every_script_has_help(self):
        for script in ("init_report.py", "census.py", "compare.py", "disclosure_check.py"):
            result = run(script, "--help")
            self.assertEqual(result.returncode, 0, script)
            self.assertIn("usage:", result.stdout, script)
        result = subprocess.run(["bash", str(SCRIPTS / "install_hooks.sh"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("pre-commit", result.stdout)


B1_QUOTE = """\
> What are the randomization-inference p-values for the six
> outcomes in Table 3, and does the footnote's procedure produce them?"""
B2_QUOTE = """\
> How many gradable activities did each arm's sections make available?
>
> - (a) as a distribution across sections;
> - (b) as a share of the activities the participation metric counts."""


class InitReportTests(TempDir):
    def init(self, *extra, host=FIXTURES / "HOST.md", prereport=FIXTURES / "PRE-REPORT.md"):
        shutil.copy(prereport, self.tmp / "PRE-REPORT.md")
        if host:
            shutil.copy(host, self.tmp / "HOST.md")
        (self.tmp / "package").mkdir(exist_ok=True)
        return run("init_report.py", "PRE-REPORT.md", *extra, cwd=self.tmp)

    def read(self, rel) -> str:
        return (self.tmp / rel).read_text(encoding="utf-8")

    def test_every_item_section_and_verbatim_questions(self):
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        report = self.read("REPORT.md")
        self.assertTrue(report.startswith(
            "# Expert Witness Report: Tutoring and Grades in a Fixture Trial\n"))
        for heading in ("### A1 — Table 3, both panels", "### B1 — Randomization inference for Table 3",
                        "### B2 — Activities available per section", "### C1 — Outcome construction"):
            self.assertEqual(report.count(f"\n{heading}\n"), 1, heading)
        self.assertIn("**Question (from the pre-report, verbatim):**\n" + B1_QUOTE + "\n\n", report)
        self.assertIn("**Question (from the pre-report, verbatim):**\n" + B2_QUOTE + "\n\n", report)
        self.assertIn("**Question (verbatim):**\n> How is each outcome built from the exports?\n\n", report)
        for row in ("| A1 | 1 | {…} | {…} |", "| B1 | 1 | {…} | {…} |", "| B2 | 2 | {…} | {…} |",
                    "| C1 | 1 | {…} | {…} |"):
            self.assertIn(row, report)
        self.assertIn("**Exhibits:** {tables/figures}", report)
        self.assertIn("**Files:** ew/items/B2/{script}, ew/items/B2/{log}, ew/items/B2/{outputs}", report)
        self.assertNotIn("not a heading", report)

    def test_skeleton_has_the_report_template_labels_and_headings(self):
        result = self.init(host=None, prereport=SKILL / "assets" / "PRE-REPORT-TEMPLATE.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        template = (SKILL / "references" / "report-template.md").read_text(encoding="utf-8")
        block = template.split("```markdown\n", 1)[1].split("\n```", 1)[0]
        report = self.read("REPORT.md")

        def shape(text):
            return (re.findall(r"^\*\*([^*]+):\*\*", text, re.M), re.findall(r"^(##? .*)$", text, re.M))
        self.assertEqual(shape(report)[0], shape(block)[0])
        self.assertEqual(shape(report)[1][1:], shape(block)[1][1:])

        def run_together(text):
            lines = text.split("\n")
            return [ln for i, ln in enumerate(lines)
                    if re.match(r"\*\*[^*]+:\*\*", ln) and i and lines[i - 1].strip()]
        self.assertEqual(run_together(block), [])
        self.assertEqual(run_together(report), [])
        self.assertIn("**Result:**\n\n{table or numbers, disclosure applied}\n\n**Finding:**", report)

    def test_template_prereport_gives_placeholder_items(self):
        text = (SKILL / "assets" / "PRE-REPORT-TEMPLATE.md").read_text(encoding="utf-8")
        title, items = init_report.parse_prereport(text)
        self.assertEqual(title, "{paper title}")
        self.assertEqual([(i["id"], i["title"]) for i in items],
                         [("A1", "{exhibit}"), ("B1", "{title}"), ("C1", "{title}")])

    def test_ew_tree_and_gitignore(self):
        self.assertEqual(self.init().returncode, 0)
        for rel in ("ew/INTAKE.md", "ew/STEPLOG.md", "ew/INTERVENTIONS.md", "ew/census/.gitkeep",
                    "ew/log/.gitkeep", "ew/reproduction/reported.csv", "ew/disclosure/allow.txt",
                    "ew/items/A1/.gitkeep", "ew/items/B1/.gitkeep", "ew/items/B2/.gitkeep",
                    "ew/items/C1/.gitkeep"):
            self.assertTrue((self.tmp / rel).is_file(), rel)
        self.assertTrue((self.tmp / "ew-local").is_dir())
        self.assertEqual(self.read("ew/reproduction/reported.csv"),
                         "table,panel,row,column,quantity,value,digits,stars\n")
        self.assertRegex(self.read("ew/STEPLOG.md"),
                         r"\n- \d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d init_report\.py run")
        intake = self.read("ew/INTAKE.md")
        for field in ("Model in use", "Effort in use", "HEAD at intake", "Branch", "Remote",
                      "PRE-REPORT.md blob", "HOST.md blob", "Package directory", "Originals",
                      "Software HOST.md says is available", "Disclosure terms in force",
                      "Supplied during the run"):
            self.assertIn(field, intake)
        interventions = self.read("ew/INTERVENTIONS.md")
        for part in ("timestamp", "**Verbatim:**", "**Kind:**", "**Response:**"):
            self.assertIn(part, interventions)
        self.assertIn("pattern|reason", self.read("ew/disclosure/allow.txt"))
        ignore = self.read(".gitignore").splitlines()
        self.assertIn("ew-local/", ignore)
        self.assertIn("package/", ignore)

    def test_existing_report_refused_and_force_keeps_the_record(self):
        self.write(".gitignore", "*.pyc\n/ew-local\n")
        self.assertEqual(self.init().returncode, 0)
        self.write("ew/INTERVENTIONS.md", "kept\n")
        again = run("init_report.py", "PRE-REPORT.md", cwd=self.tmp)
        self.assertEqual(again.returncode, 1)
        self.assertIn("already exists", again.stderr)
        forced = run("init_report.py", "PRE-REPORT.md", "--force", cwd=self.tmp)
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertEqual(self.read("ew/INTERVENTIONS.md"), "kept\n")
        self.assertEqual(self.read("ew/STEPLOG.md").count("init_report.py run"), 2)
        self.assertEqual(self.read(".gitignore"),
                         "*.pyc\n/ew-local\n\n# expert-witness (init_report.py): never committed\npackage/\n")

    def test_missing_host_or_field_warns_loudly(self):
        result = self.init(host=None)
        self.assertEqual(result.returncode, 0)
        self.assertIn("WARNING: HOST.md not found", result.stderr)
        self.assertEqual([ln for ln in self.read(".gitignore").splitlines() if ln and ln[0] != "#"],
                         ["ew-local/"])
        self.write("HOST.md", "# Host declaration\n\n- **Host:** authors\n")
        result = run("init_report.py", "PRE-REPORT.md", "--force", cwd=self.tmp)
        self.assertIn("WARNING: HOST.md has no **Package directory:** field", result.stderr)
        shutil.copy(SKILL / "assets" / "HOST-TEMPLATE.md", self.tmp / "HOST.md")
        result = run("init_report.py", "PRE-REPORT.md", "--force", cwd=self.tmp)
        self.assertIn("still the placeholder", result.stderr)

    def test_missing_package_directory_warns_loudly(self):
        shutil.copy(FIXTURES / "PRE-REPORT.md", self.tmp / "PRE-REPORT.md")
        shutil.copy(FIXTURES / "HOST.md", self.tmp / "HOST.md")
        result = run("init_report.py", "PRE-REPORT.md", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING: the package directory package/ read from HOST.md does not exist",
                      result.stderr)
        self.assertIn("package/", self.read(".gitignore").splitlines())

    def test_package_dir_variants(self):
        cases = {"- **Package directory:** `package/`": "package",
                 "- **Package directory:** ./copy/pkg/ (a copy)": "copy/pkg",
                 f"- **Package directory:** {self.tmp / 'abs'}": "abs",
                 "- **Package directory:** /elsewhere/package": None,
                 "- **Package directory:** ../outside": None,
                 "- **Package directory:** {path, relative to the run directory}": None}
        for line, expected in cases.items():
            host = self.write("HOST.md", f"# Host declaration\n\n{line}\n  (`init_report.py` note)\n")
            self.assertEqual(init_report.package_dir_from_host(host, self.tmp)[0], expected, line)

    def test_malformed_prereports_are_refused(self):
        good = "# Pre-report: T\n\n### B1 — Fine\n\n**Question:** Q?\n"
        cases = {"no items": ("# Pre-report: T\n\nNothing here.\n", "no items found"),
                 "colon": (good + "\n### B2: Colon\n", "must be followed by ' — '"),
                 "level": (good + "\n#### B2 — Too deep\n", "level 3"),
                 "en dash": (good + "\n### B2 – En dash\n", "not an en dash"),
                 "lower case": (good + "\n### b2 — Lower\n", "not an item ID"),
                 "no title": (good + "\n### B2 —\n", "title after the dash is missing"),
                 "duplicate": (good + "\n### B1 — Again\n", "already appears"),
                 "no title heading": ("### B1 — Fine\n\n**Question:** Q?\n", "no '# Pre-report:"),
                 "open fence": (good + "\n```\n### B2 — Hidden\n", "never closed")}
        for name, (text, phrase) in cases.items():
            with self.subTest(name):
                self.write("PRE-REPORT.md", text)
                result = run("init_report.py", "PRE-REPORT.md", cwd=self.tmp)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(phrase, result.stderr)
                self.assertIn("PRE-REPORT-TEMPLATE.md", result.stderr)
                self.assertFalse((self.tmp / "REPORT.md").exists())

    def test_skeleton_passes_the_disclosure_checker(self):
        self.assertEqual(self.init().returncode, 0)
        result = run("disclosure_check.py", "REPORT.md", "ew", ".gitignore", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout)


class CensusTests(TempDir):
    def setUp(self):
        super().setUp()
        self.pkg = self.tmp / "package"
        shutil.copytree(FIXTURES / "package", self.pkg)
        self.write(".git/config", "[core]\n", base=self.pkg)
        self.out = self.tmp / "ew" / "census"

    def census(self, env=None) -> dict:
        result = run("census.py", self.pkg, "--out", self.out, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((self.out / "census.json").read_text(encoding="utf-8"))

    def test_hashes_sizes_and_types(self):
        doc = self.census()
        on_disk = sorted(p.relative_to(self.pkg).as_posix() for p in self.pkg.rglob("*")
                         if p.is_file() and ".git" not in p.relative_to(self.pkg).parts)
        self.assertEqual([r["path"] for r in doc["files"]], on_disk)
        for rec in doc["files"]:
            data = (self.pkg / rec["path"]).read_bytes()
            self.assertEqual(rec["sha256"], hashlib.sha256(data).hexdigest(), rec["path"])
            self.assertEqual(rec["bytes"], len(data), rec["path"])
        types = {r["path"]: r["type"] for r in doc["files"]}
        self.assertEqual([types[p] for p in ("code/master.do", "code/analysis.R", "data/scores.csv",
                                             "code/make_figures.py", "Makefile")],
                         ["do", "R", "csv", "py", "other"])
        summary = doc["summary"]
        self.assertEqual(summary["file_count"], len(on_disk))
        self.assertEqual(summary["total_bytes"], sum(r["bytes"] for r in doc["files"]))
        self.assertEqual(summary["languages"], ["Python", "R", "Stata"])

    def test_entry_points_and_calls(self):
        eps = {e["path"]: e for e in self.census()["summary"]["entry_points"]}
        self.assertEqual(eps["code/master.do"]["calls"], ["01_clean.do", "$root/code/02_tables"])
        self.assertIn("named like an entry point", eps["code/master.do"]["why"])
        self.assertEqual(eps["code/analysis.R"]["calls"], ["helpers.R"])
        self.assertEqual(eps["code/make_figures.py"]["calls"], ["plot_helpers.py"])
        self.assertEqual(eps["Makefile"]["calls"], ["master.do"])
        self.assertNotIn("code/01_clean.do", eps)
        text = (self.out / "CENSUS.md").read_text(encoding="utf-8")
        for heading in ("## Files by type", "## The 30 largest files", "## Candidate entry points",
                        "## Software on this machine"):
            self.assertIn(heading, text)
        self.assertIn("| `code/master.do` | named like an entry point; calls other do-files "
                      "| `01_clean.do`", text)

    def test_never_executes_programs(self):
        sentinel = self.tmp / "ran.txt"
        fake = f'#!/bin/sh\necho ran >> "{sentinel}"\necho "fake 1.0"\n'
        stata, r_inside = self.write("bin/stata-mp", fake), self.write("bin/R", fake, base=self.pkg)
        for path in (stata, r_inside):
            path.chmod(0o755)
        env = dict(os.environ, PATH=os.pathsep.join([str(stata.parent), str(r_inside.parent),
                                                     os.environ.get("PATH", "")]))
        found = {s["name"]: s for s in self.census(env=env)["summary"]["software"]}
        self.assertFalse(sentinel.exists(), "census.py ran a program")
        self.assertEqual(found["stata-mp"]["where"], str(stata))
        self.assertIn("not launched", found["stata-mp"]["how"])
        self.assertEqual(found["R"]["how"], "inside the package; not run")
        self.assertTrue((self.pkg / "code" / "sentinel.txt").exists())

    def test_stata_bundle_version_from_info_plist(self):
        contents = self.tmp / "Applications" / "Stata" / "StataMP.app" / "Contents"
        (contents / "MacOS").mkdir(parents=True)
        with open(contents / "Info.plist", "wb") as fh:
            plistlib.dump({"CFBundleShortVersionString": "18.5", "CFBundleName": "StataMP"}, fh)
        found = census.stata_bundles(str(self.tmp / "Applications"))
        self.assertEqual([(b["name"], b["version"]) for b in found], [("StataMP", "18.5")])

    def test_out_inside_package_is_refused(self):
        result = run("census.py", self.pkg, "--out", self.pkg / "census")
        self.assertEqual(result.returncode, 2)
        self.assertIn("inside the package", result.stderr)
        self.assertFalse((self.pkg / "census").exists())

    def test_census_output_passes_the_disclosure_checker(self):
        self.census()
        result = run("disclosure_check.py", self.out, "--allow", self.tmp / "none",
                     "--terms", self.tmp / "none")
        self.assertEqual(result.returncode, 0, result.stdout)


class CompareTests(TempDir):
    EXPECTED = {
        ("Table 3", "A", "Treated", "(1)", "coef"): ("MATCH", False),
        ("Table 3", "A", "Treated", "(1)", "se"): ("MATCH", False),
        ("Table 3", "A", "Treated", "(2)", "coef"): ("MATCH", False),
        ("Table 3", "A", "Treated", "(3)", "coef"): ("WITHIN-ONE-UNIT", False),
        ("Table 3", "A", "Treated", "(4)", "coef"): ("DIFFERS", False),
        ("Table 3", "A", "Observations", "(1)", "n"): ("MATCH", False),
        ("Table 3", "A", "Observations", "(2)", "n"): ("DIFFERS", False),
        ("Table 3", "B", "Treated", "(1)", "coef"): ("MATCH", True),
        ("Table 3", "B", "Treated", "(2)", "coef"): ("MISSING-IN-REPRODUCED", False),
        ("Table 2", "", "Used VSA", "Treated", "mean"): ("MATCH", False),
        ("Table 2", "", "p-value", "Treated", "p"): ("NOT-NUMERIC", False),
        ("Table 3", "A", "Treated", "(5)", "coef"): ("EXTRA", False),
    }

    def test_statuses_come_out_as_planted(self):
        for name in ("reported.csv", "reproduced.csv"):
            shutil.copy(FIXTURES / name, self.tmp / name)
        result = run("compare.py", self.tmp / "reported.csv", self.tmp / "reproduced.csv")
        self.assertEqual(result.returncode, 0, result.stderr)
        reported, stars_rep = compare.read_cells(self.tmp / "reported.csv",
                                                 compare.KEYS + ("value", "digits"))
        reproduced, stars_pro = compare.read_cells(self.tmp / "reproduced.csv",
                                                   compare.KEYS + ("value",))
        results = compare.compare(reported, reproduced, stars_rep and stars_pro)
        got = {r["key"]: (r["status"], "STARS-DIFFER" in r["flags"]) for r in results}
        self.assertEqual(got, self.EXPECTED)
        text = (self.tmp / "COMPARE.md").read_text(encoding="utf-8")
        self.assertIn("### Table 3\n\n- 6 of 9 cells within tolerance", text)
        self.assertIn("### Table 2\n\n- 1 of 2 cells within tolerance", text)
        self.assertIn("Largest absolute difference: 1 at A / Observations / (2) / n", text)
        self.assertIn("Largest relative difference: 75.00% at A / Treated / (4) / coef", text)
        for status in compare.STATUSES + ("STARS-DIFFER",):
            self.assertIn(f"| {status} |" if status != "STARS-DIFFER" else "STARS-DIFFER |", text)
        self.assertIn("Table 3: 6 of 9 cells within tolerance (MATCH 5, WITHIN-ONE-UNIT 1, DIFFERS 2, "
                      "MISSING-IN-REPRODUCED 1, NOT-NUMERIC 0, EXTRA 1; STARS-DIFFER 1)", result.stdout)

    def test_rounding_examples_from_running_code_md(self):
        cases = [("-2.88", 2, "-2.8849", "MATCH"), ("0.02", 2, "0.0151", "MATCH"),
                 ("0.02", 2, "0.0249", "MATCH"), ("0.02", 2, "0.025", "WITHIN-ONE-UNIT"),
                 ("0.02", 2, "0.034", "WITHIN-ONE-UNIT"), ("0.02", 2, "0.0149", "WITHIN-ONE-UNIT"),
                 ("0.02", 2, "0.035", "DIFFERS"), ("2379", 0, "2380", "WITHIN-ONE-UNIT")]
        for printed, digits, value, status in cases:
            self.assertEqual(compare.classify(Decimal(printed), digits, Decimal(value))[0], status,
                             (printed, value))
        for text, value in (("(0.95)", "0.95"), ("2,379", "2379"), ("\u22120.12", "-0.12"),
                            ("[1.5]", "1.5"), ("<0.001", None), ("", None), ("0,153", None)):
            parsed = compare.parse_number(text)
            self.assertEqual(parsed, Decimal(value) if value else None, text)

    def test_counts_must_match_exactly(self):
        for printed, value, count, status in (("2379", "2380", True, "DIFFERS"),
                                              ("2379", "2378", True, "DIFFERS"),
                                              ("2379", "2379.0", True, "MATCH"),
                                              ("2379", "2379.4", True, "DIFFERS"),
                                              ("2379", "2380", False, "WITHIN-ONE-UNIT")):
            got = compare.classify(Decimal(printed), 0, Decimal(value), count=count)[0]
            self.assertEqual(got, status, (printed, value, count))
        reported = self.write("rep.csv", 'table,panel,row,column,quantity,value,digits\n'
                                         'T,,N,(1),n,"2,379",0\nT,,Mean,(1),mean,2379,0\n')
        reproduced = self.write("pro.csv", "table,panel,row,column,quantity,value\n"
                                           "T,,N,(1),n,2380\nT,,Mean,(1),mean,2380\n")
        result = run("compare.py", reported, reproduced, "--out", self.tmp / "C.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.tmp / "C.md").read_text(encoding="utf-8")
        self.assertIn("| T |  | N | (1) | n | 2,379 | 0 | 2380 | 2380 | DIFFERS |", text)
        self.assertIn("| T |  | Mean | (1) | mean | 2379 | 0 | 2380 | 2380 | WITHIN-ONE-UNIT |", text)

    def test_input_errors_exit_2(self):
        bad = self.write("bad.csv", "table,value\nT1,1\n")
        dup = self.write("dup.csv", "table,panel,row,column,quantity,value,digits\nT,A,r,c,coef,1,0\n"
                                    "T,A,r,c,coef,2,0\n")
        for args, phrase in (((bad, FIXTURES / "reproduced.csv"), "lacks the column"),
                             ((dup, FIXTURES / "reproduced.csv"), "repeats the key"),
                             ((self.tmp / "absent.csv", FIXTURES / "reproduced.csv"), "cannot read")):
            result = run("compare.py", *args, "--out", self.tmp / "C.md")
            self.assertEqual(result.returncode, 2, phrase)
            self.assertIn(phrase, result.stderr)


PLANTS = [("report_with_hits.md", "email", "jane.doe@example.edu"),
          ("report_with_hits.md", "phone", "(555) 010-0199"),
          ("report_with_hits.md", "long-id", "90210537"),
          ("report_with_hits.md", "course-code", "ECON 201"),
          ("report_with_hits.md", "term", "Quillfeather"),
          ("report_with_hits.md", "small-cell", "| Humanities | 7 |"),
          ("report_with_hits.md", "quote", "the tutor kept giving me"),
          ("listing.log", "listing", "1. |")]


def planted(skip=()) -> set:
    expected = set()
    for name, rule, marker in PLANTS:
        if rule in skip:
            continue
        lines = (DISC / name).read_text(encoding="utf-8").splitlines()
        numbers = [n for n, line in enumerate(lines, 1) if marker in line]
        assert len(numbers) == 1, (name, marker)
        expected.add((name, numbers[0], rule))
    return expected


class DisclosureTests(TempDir):
    def check(self, *paths, allow=None, terms=DISC / "sensitive-terms.txt", extra=()):
        return run("disclosure_check.py", *paths, "--allow", allow or self.tmp / "no-allow.txt",
                   "--terms", terms, *extra)

    def test_reports_exactly_the_planted_hits(self):
        result = self.check(DISC / "report_with_hits.md", DISC / "listing.log")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(hits_of(result), planted())

    def test_allow_file_suppresses_exactly_one(self):
        result = self.check(DISC / "report_with_hits.md", DISC / "listing.log", allow=DISC / "allow.txt")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(hits_of(result), planted(skip=("course-code",)))
        self.assertIn("1 hit(s) suppressed", result.stdout)

    def test_exit_0_once_every_hit_is_allowed(self):
        allow = self.write("allow.txt", "".join(f"{marker}|planted fixture hit\n" for _, _, marker in PLANTS))
        result = self.check(DISC / "report_with_hits.md", DISC / "listing.log", allow=allow)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("result: PASS", result.stdout)

    def test_scoped_allow_entry_suppresses_only_its_rule(self):
        notes = self.write("notes.md", "Contact jane.doe@example.edu about record 90210537 today.\n")
        both = {("notes.md", 1, "email"), ("notes.md", 1, "long-id")}
        self.assertEqual(hits_of(self.check(notes)), both)
        # The pattern is in the excerpt of both hits; the scope decides which one it clears.
        scoped = self.write("scoped.txt", "long-id:jane.doe@example.edu|scoped to long-id\n")
        result = self.check(notes, allow=scoped)
        self.assertEqual(hits_of(result), {("notes.md", 1, "email")})
        self.assertEqual(result.returncode, 1)
        unscoped = self.write("unscoped.txt", "jane.doe@example.edu|the older form covers every rule\n")
        result = self.check(notes, allow=unscoped)
        self.assertEqual((hits_of(result), result.returncode), (set(), 0))
        not_a_rule = self.write("typo.txt", "long_id:90210537|not a rule name, so read as a pattern\n")
        result = self.check(notes, allow=not_a_rule)
        self.assertEqual(hits_of(result), both)
        self.assertIn("'long_id' is not a rule name (email, phone, long-id, course-code, term, "
                      "small-cell, quote, listing)", result.stderr)

    def test_pre_report_quotes_are_exempt_and_novel_quotes_are_not(self):
        pre = self.write("PRE-REPORT.md", '**Paper\'s statement at issue:** "We therefore also conducted '
                         'randomization\ninference, re-randomizing treatment across instructors within '
                         'randomization block." (p. 19)\n')
        report = self.write("REPORT.md", 'The pre-report cites: "We therefore also conducted randomization '
                            'inference, re-randomizing treatment across instructors within randomization '
                            'block." (p. 19).\nOne student wrote "the tutor kept giving me the answer '
                            'before I had even tried to think about it" in the survey.\n')
        both = {("REPORT.md", 1, "quote"), ("REPORT.md", 2, "quote")}
        self.assertEqual(hits_of(self.check(report)), both)
        result = self.check(report, extra=("--pre-report", pre))
        self.assertEqual(hits_of(result), {("REPORT.md", 2, "quote")})
        self.assertIn("pre-report: 1 quoted span(s) found in", result.stdout)
        absent = self.check(report, extra=("--pre-report", self.tmp / "absent.md"))
        self.assertEqual(hits_of(absent), both)
        self.assertIn("not found; no quoted span is exempted", absent.stdout)

    def test_absent_terms_file_is_reported(self):
        result = self.check(DISC / "report_with_hits.md", terms=self.tmp / "absent.txt")
        self.assertNotIn("term", {rule for _, _, rule in hits_of(result)})
        self.assertIn("terms: rule skipped", result.stdout)

    def test_small_cells_inline_csv_and_markdown(self):
        self.write("notes.txt", "Treated: n = 7 students\nn = 1,234\nN=12\nn = 0.5\nfor n == 3\n")
        self.write("counts.csv", "block,n_students,share,mean\nA,4,3,0.5\nB,40,7,0.6\n")
        self.write("table.md", "| Group | Respondents | Coefficient |\n|---|---|---|\n"
                               "| a | 9 | 7 |\n| b | 12 | 3 |\n")
        result = self.check(self.tmp / "notes.txt", self.tmp / "counts.csv", self.tmp / "table.md")
        self.assertEqual(hits_of(result), {("notes.txt", 1, "small-cell"), ("counts.csv", 2, "small-cell"),
                                           ("table.md", 3, "small-cell")})

    def test_long_id_exemptions(self):
        digest = "0123456789" * 6 + "abcd"
        self.write("ids.md", f"census {digest}\ncommit 1234567abcdef1234567abcdef1234567abcdef0\n"
                             "p = 0.1234567\nUID 1234567\nlogin U12345678\nrecord 90210537.\n"
                             "b = .1234567 and total 1234567.89\n")
        result = self.check(self.tmp / "ids.md")
        self.assertEqual(hits_of(result), {("ids.md", 4, "long-id"), ("ids.md", 5, "long-id"),
                                           ("ids.md", 6, "long-id")})

    def test_skips_git_ew_local_binary_and_symlinks(self):
        tree = self.tmp / "tree"
        for rel in (".git/config", "ew-local/terms.txt", "data.dta"):
            self.write(rel, "jane.doe@example.edu\n", base=tree)
        (tree / "blob.bin").write_bytes(b"\0jane.doe@example.edu\n")
        self.write("ok.md", "Aggregates only.\n", base=tree)
        os.symlink(tree / "data.dta", tree / "link.md")
        if hasattr(os, "mkfifo"):
            os.mkfifo(tree / "pipe.md")
        result = self.check(tree)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("scanned 1 file(s)", result.stdout)
        self.assertIn("not scanned (binary): 2", result.stdout)
        self.assertIn("not scanned (symbolic link): 1", result.stdout)
        if hasattr(os, "mkfifo"):
            self.assertIn("not scanned (not a regular file): 1", result.stdout)
        named = self.check(tree / "ew-local" / "terms.txt")
        self.assertEqual(named.returncode, 0)
        self.assertIn("not scanned (under .git/ or ew-local/): 1", named.stdout)

    def test_listing_rule_is_for_logs_and_catches_r_prints(self):
        frame = "  id score treat\n1 101 78 1\n2 102 85 0\n3 103 91 1\n"
        self.write("r.log", frame)
        self.write("r.txt", frame)
        result = self.check(self.tmp / "r.log", self.tmp / "r.txt")
        self.assertEqual(hits_of(result), {("r.log", 2, "listing")})

    def test_quiet_prints_only_the_summary(self):
        result = self.check(DISC / "report_with_hits.md", extra=("--quiet",))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(hits_of(result), set())
        self.assertIn("hits not allowed: email 1", result.stdout)
        self.assertIn("result: FAIL", result.stdout)

    def test_seeded_allow_covers_census_file_sizes(self):
        census_json = self.write("census.json", '{\n  "bytes": 47812345,\n  "total_bytes": 98765432\n}\n')
        self.assertEqual(hits_of(self.check(census_json)), {("census.json", 2, "long-id"),
                                                            ("census.json", 3, "long-id")})
        result = self.check(census_json, allow=SCRIPTS / "templates" / "allow.txt")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_path_is_a_usage_error(self):
        result = self.check(self.tmp / "absent.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no such file", result.stderr)


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "needs git and bash")
class HookTests(TempDir):
    def setUp(self):
        super().setUp()
        home, self.repo = self.tmp / "home", self.tmp / "run"
        home.mkdir()
        self.repo.mkdir()
        self.env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CEILING_DIRECTORIES=str(self.tmp),
                        GIT_AUTHOR_NAME="EW Test", GIT_AUTHOR_EMAIL="ew-test@example.invalid",
                        GIT_COMMITTER_NAME="EW Test", GIT_COMMITTER_EMAIL="ew-test@example.invalid")
        self.git("init", "-q")
        self.hook = self.repo / ".git" / "hooks" / "pre-commit"

    def git(self, *args, check=True):
        result = subprocess.run(["git", *args], cwd=self.repo, env=self.env, capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def install(self, cwd=None):
        return subprocess.run(["bash", str(SCRIPTS / "install_hooks.sh")], cwd=cwd or self.repo,
                              env=self.env, capture_output=True, text=True)

    def commit(self, *paths, force=False):
        if paths:
            self.git("add", *(["-f"] if force else []), *paths)
        result = self.git("commit", "-q", "-m", "test", check=False)
        return result.returncode, result.stdout + result.stderr

    def test_not_a_git_repository(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        result = self.install(cwd=plain)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not inside a git work tree", result.stderr)

    def test_installs_an_executable_hook_with_absolute_paths(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.access(self.hook, os.X_OK))
        self.assertIn(f"EW_SCRIPTS='{SCRIPTS}'", self.hook.read_text())

    def test_blocks_a_staged_ew_local_file(self):
        self.assertEqual(self.install().returncode, 0)
        self.write("ew-local/sensitive-terms.txt", "Quillfeather\n", base=self.repo)
        status, output = self.commit("ew-local/sensitive-terms.txt", force=True)
        self.assertNotEqual(status, 0)
        self.assertIn("ew-local/sensitive-terms.txt  (under ew-local/)", output)
        self.assertNotEqual(self.git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode, 0)

    def test_blocks_the_package_directory_named_in_host_md(self):
        self.assertEqual(self.install().returncode, 0)
        shutil.copy(FIXTURES / "HOST.md", self.repo / "HOST.md")
        self.write("package/data/scores.csv", "block,score\n1,70\n", base=self.repo)
        status, output = self.commit("HOST.md", "package/data/scores.csv")
        self.assertNotEqual(status, 0)
        self.assertIn("under the package directory package/", output)

    def test_blocks_a_disclosure_hit_and_allows_a_clean_commit(self):
        self.assertEqual(self.install().returncode, 0)
        self.write("notes.md", "Contact jane.doe@example.edu for the export.\n", base=self.repo)
        status, output = self.commit("notes.md")
        self.assertNotEqual(status, 0)
        self.assertIn("notes.md:1: email:", output)
        self.assertIn("commit blocked by the disclosure check", output)
        self.git("rm", "-q", "--cached", "notes.md")
        self.write("clean.md", "Aggregates only; every cell has at least ten students.\n", base=self.repo)
        status, output = self.commit("clean.md")
        self.assertEqual(status, 0, output)

    def test_checks_the_staged_content_not_the_working_tree(self):
        self.assertEqual(self.install().returncode, 0)
        self.write("leak.md", "Contact jane.doe@example.edu\n", base=self.repo)
        self.git("add", "leak.md")
        self.write("leak.md", "Contact the data manager.\n", base=self.repo)
        status, output = self.commit()
        self.assertNotEqual(status, 0)
        self.assertIn("leak.md:1: email:", output)
        self.git("add", "leak.md")
        self.write("leak.md", "Contact jane.doe@example.edu\n", base=self.repo)
        status, output = self.commit()
        self.assertEqual(status, 0, output)

    def test_hook_exempts_quotes_from_the_pre_report(self):
        sentence = ("Our conclusions are robust to this approach, which re-randomizes treatment "
                    "across instructors within each block.")
        self.write("PRE-REPORT.md", f'**Paper\'s statement at issue:** "{sentence}" (p. 19)\n', base=self.repo)
        self.assertEqual(self.commit("PRE-REPORT.md")[0], 0)
        self.assertEqual(self.install().returncode, 0)
        self.assertIn("--pre-report", self.hook.read_text())
        self.write("REPORT.md", f'The pre-report cites: "{sentence}" (p. 19).\n', base=self.repo)
        status, output = self.commit("REPORT.md")
        self.assertEqual(status, 0, output)
        self.write("REPORT.md", 'A student wrote "the tutor kept giving me the answer before I had even '
                   'tried to think" in the survey.\n', base=self.repo)
        status, output = self.commit("REPORT.md")
        self.assertNotEqual(status, 0)
        self.assertIn("REPORT.md:1: quote:", output)

    def test_hook_reads_the_committed_pre_report(self):
        committed = ("Our conclusions are robust to this approach, which re-randomizes treatment "
                     "across instructors within each block.")
        added = ("The tutor kept giving me the answer before I had even tried to think about the "
                 "problem set.")
        self.write("PRE-REPORT.md", f'"{committed}"\n', base=self.repo)
        self.assertEqual(self.commit("PRE-REPORT.md")[0], 0)
        self.assertEqual(self.install().returncode, 0)
        self.write("PRE-REPORT.md", f'"{committed}"\n"{added}"\n', base=self.repo)  # not committed
        self.write("REPORT.md", f'Quoted: "{added}"\n', base=self.repo)
        status, output = self.commit("REPORT.md")
        self.assertNotEqual(status, 0)
        self.assertIn("REPORT.md:1: quote:", output)
        self.write("REPORT.md", f'Quoted: "{committed}"\n', base=self.repo)
        status, output = self.commit("REPORT.md")
        self.assertEqual(status, 0, output)

    def test_hook_uses_the_working_tree_pre_report_before_the_first_commit(self):
        self.assertEqual(self.install().returncode, 0)
        sentence = ("Our conclusions are robust to this approach, which re-randomizes treatment "
                    "across instructors within each block.")
        self.write("PRE-REPORT.md", f'"{sentence}"\n', base=self.repo)
        self.write("REPORT.md", f'Quoted: "{sentence}"\n', base=self.repo)
        status, output = self.commit("PRE-REPORT.md", "REPORT.md")
        self.assertEqual(status, 0, output)
        self.assertIn("no commit yet, so --pre-report uses the working-tree PRE-REPORT.md", output)

    def test_hooks_path_elsewhere_is_refused(self):
        self.git("config", "core.hooksPath", "elsewhere")
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("core.hooksPath", result.stderr)
        self.assertFalse(self.hook.exists())

    def test_reinstall_replaces_its_own_hook_and_keeps_a_foreign_one(self):
        self.write(".git/hooks/pre-commit", "#!/bin/sh\nexit 0\n", base=self.repo)
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.install().returncode, 0)
        kept = self.repo / ".git" / "hooks" / "pre-commit.before-expert-witness"
        self.assertEqual(kept.read_text(), "#!/bin/sh\nexit 0\n")
        self.assertIn("expert-witness pre-commit hook", self.hook.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
