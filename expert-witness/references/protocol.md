# Protocol: the phases in detail, and what to do when things go wrong

Read this once before phase 1. It is organized as the run is. The short
version of every rule here is the same: do the literal thing the pre-report
asks, record what you did, and when you cannot, say so in the report rather
than improvising around it.

## Contents

1. Intake (phase 0)
2. Census (phase 1)
3. Read (phase 2)
4. Reproduce (phase 3)
5. Items (phase 4)
6. Disclosure review (phase 5)
7. Release (phase 6)
8. Decision rules A–N: software missing, code will not run, network, side
   effects, manual steps, data differ from the paper, randomness, long jobs,
   ambiguous items, errors in the pre-report, host-supplied data, budget,
   units and conventions, partial completion

---

## 1. Intake (phase 0)

`ew/INTAKE.md` records, before anything else happens:

- Date and time the run started; your model id as you know it; the effort
  setting if the host told you; the pre-report's requested model and effort.
- `git rev-parse HEAD`, the branch, the remote URL (with any token removed),
  and the blob hashes of `PRE-REPORT.md` and `HOST.md`.
- The package directory, the originals path if any, and the software
  `HOST.md` says is available.
- The disclosure terms that govern: the pre-report's defaults, `HOST.md`'s
  terms, and which is stricter on each point.

If `HOST.md` lists a `sensitive-terms` file, confirm it is under `ew-local/`
and gitignored. If it is anywhere else, move it there before the first
commit; the file is the one thing in the run that must never be pushed.

## 2. Census (phase 1)

`scripts/census.py` walks the package and writes `ew/census/census.json`
(every file: relative path, bytes, SHA-256, detected type) and `CENSUS.md`
(counts by type, candidate entry points, software found on the machine with
versions). It never executes package code. Read `CENSUS.md`; if the package
contains things the pre-report says it should not (student rosters, chat
logs with text), note it in INTAKE and do not open those files except as
the pre-report's items require, and then only through scripts that output
aggregates.

## 3. Read (phase 2)

Read every script, including ones that look unrelated; the pre-report's
questions often turn on a line in a data-cleaning file. `ew/CODE-MAP.md`
holds:

- **Entry points and order.** Master scripts, or the order you inferred and
  why.
- **Table and figure map.** For each exhibit in Part A: script, line range,
  output file.
- **Data flow.** Raw inputs → intermediate files → analysis file, with the
  script and the merge keys at each step. Which files in the package are
  raw, which are intermediate, which are outputs.
- **Exclusions and constructions.** Every sample restriction (with the line
  of code), every outcome and covariate construction the items depend on,
  every hard-coded number (a manually entered N, a date, a threshold).
- **Side effects.** Every deletion, overwrite, write outside the package,
  shell-out, network call, and package install, with file and line.
- **Manual steps.** Anything the README or comments say was done by hand.
- **Run plan.** What you will run, in what order, with what neutralizations
  (see rule D).

## 4. Reproduce (phase 3)

Run the pipeline as the authors would, in the copy, in batch mode, with the
working directory and root paths set to the copy. Capture every log under
`ew/log/`, named for the script. Record the command, start, end, and exit
status in `STEPLOG.md`.

`ew/reproduction/reported.csv` is your transcription of the paper's cells:
one row per cell, columns `table,panel,row,column,quantity,value,digits`
where `quantity` is `coef`, `se`, `n`, `sd`, `mean`, `p`, or `other` and
`digits` is the number of decimals printed. Transcribe exactly what is
printed, including the sign and the stars in a separate `stars` column if
present. `reproduced.csv` has the same keys and the pipeline's value at full
precision. `scripts/compare.py` matches on keys and writes `COMPARE.md`.

Tolerance: a reproduced value is within tolerance if, rounded to the
paper's printed digits, it equals the printed value, or differs by one unit
in the last digit (rounding-mode differences). Counts (`quantity` = `n`)
have no rounding, so only an exact match counts; a count off by one is
`DIFFERS` and usually means a sample-construction difference worth an
Observation. Anything else is `DIFFERS`, and the comparison shows the two
values side by side.

If the package produces the table from an intermediate file rather than
from raw data (rule E), the finding says which: "REPRODUCED from the
analysis file `analysis.dta`; the raw-to-analysis step was not run because
…".

## 5. Items (phase 4)

Tier order from the pre-report, then ID order. For each item:

1. Read its specification twice. Write down the literal reading. If two
   readings are possible, the literal one is primary; the second is reported
   if it costs little, labeled as the alternative reading.
2. Write the script under `ew/items/<ID>/`. Set seeds; record them. Use the
   authors' analysis file and variable definitions unless the item says
   otherwise; where you reconstruct a variable, say so and say how.
3. Run it; capture the log.
4. Apply disclosure to every output before it is written anywhere under
   `ew/items/<ID>/`. Suppressed cells show `<min` (for example `<10`), never
   a blank that could be read as zero.
5. Fill the section in `REPORT.md`. The "Bearing on the paper's statement"
   line quotes the sentence the pre-report cites, page number included.
6. Commit and push: `EW: item <ID>`.

Do not start an item by looking for what would make it come out one way.
Start by computing the quantity. Then compare.

## 6. Disclosure review (phase 5)

The pre-commit hook has run the checker on every commit. The whole-report
pass is different: read `REPORT.md` and every committed output as a
stranger would, with the checklist in `disclosure.md`, and record each
answer in `ew/disclosure/CHECK.md`. Then re-run the checker on the whole
`ew/` tree and `REPORT.md` and paste its output into `CHECK.md`.

## 7. Release (phase 6)

Fill the summary table. Set the status line. Commit `EW: release v1`, tag
`report-v1`, push the branch and the tag. After the tag, `REPORT.md` is
frozen; `REPORT-ERRATA.md` with `report-v1.1` is how corrections happen.
Record the end time and per-phase wall-clock in `INTAKE.md`'s run block.

---

## 8. Decision rules

**A. Software is missing** (no Stata license, no R, wrong Python). Part A
tables that need it are `COULD-NOT-RUN` with the software named. Do not
translate the authors' code into another language to reproduce a table
unless the pre-report says re-implementation is acceptable; a translation
is a re-implementation and is labeled as one, with the diff in logic
described. Part B items you can do in whatever is available; say what you
used.

**B. The code errors out.** Read the error. If it is an environment fault
(path, missing package the host allows you to install, version
incompatibility with a one-line fix), fix it in the copy, record the diff
under `ew/log/<script>.patch`, and continue. If it is a logic fault (the
code as shipped cannot produce the table), stop that script, report
`COULD-NOT-RUN` with the error, and continue with the next.

**C. The code needs the network.** `ssc install`, `install.packages`,
`pip install`, downloads of data. Allowed only as `HOST.md` allows; record
every install with the version obtained. Data downloads are never allowed;
if a script fetches data at runtime, it is `COULD-NOT-RUN` unless the host
supplies the file (rule K).

**D. Side effects.** A script that deletes files, writes outside the package,
or shells out is run only after the side effect is neutralized in the copy
(comment out the line, redirect the path), with the change recorded as a
patch. A script whose entire purpose is a side effect (a cleanup script) is
not run.

**E. Manual steps.** If the README documents a hand step (an Excel edit, a
value typed in), replicate it in a script, label it, and say what you did.
If an undocumented hand step is implied (an intermediate file the code
reads but no script writes), run from the intermediate file, say so in the
finding, and list the step under Observations.

**F. The data differ from the paper's description.** Ns, dates, variable
lists. Report the numbers you see next to the numbers the paper prints, in
the item they bear on. Do not reconcile them yourself beyond what the
pre-report asks.

**G. Randomness.** Set and record seeds in your scripts. If the authors'
code has an unseeded random step that affects a reported number, note it
and run it three times; report the range.

**H. Long jobs.** Run in the background with the log tailed; record the
runtime. If the host's budget in `HOST.md` would be exceeded, finish the
current item, mark the rest `NOT-ATTEMPTED (budget)`, and release.

**I. The item is ambiguous.** Literal reading first. The requester is not in
the room and cannot be asked; the host can be asked only for facts about
the data and the environment, never for what the requester meant.

**J. The pre-report is wrong about the paper** (cites a table that does not
exist, misquotes a page). Do the nearest thing that is obviously intended if
there is one, say what you did and why, and quote the discrepancy. If there
is no obvious intent, `NOT-ANSWERABLE` with the reason.

**K. The host supplies data or files during the run** (a Canvas export that
was not in the package, the OSF document). Accept as a clarification of
fact: hash the file, add it to `ew/INTAKE.md` under "Supplied during the
run", record the intervention, and say in every item that uses it that the
input was supplied by the host during the run. Never accept a replacement
for a file already in the package without recording both hashes.

**L. Budget and tiers.** If the pre-report is tiered and `HOST.md` sets a
budget, release `report-v1` when tier 1 is done, then continue. Status
`PARTIAL` lists the items outstanding.

**M. Units and conventions.** Report in the paper's own units and, where the
paper does, in control-group standard deviations computed the same way the
paper computes them (say how). Match the paper's clustering and controls
unless the item asks for something else, and then report both.

**N. Partial completion and stops.** Whatever the reason, the state of the
repository at the end of the run is the report. Commit, set the status
line, push. Never leave work uncommitted on the host's machine.
