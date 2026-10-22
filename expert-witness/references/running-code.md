# Running the authors' code

## Reading before running

Open every script and look for, in this order:

| Language | Destructive | Outside the package | Network / installs | Shell |
|---|---|---|---|---|
| Stata | `erase`, `rm`, `rmdir`, `save … , replace` to a path outside the copy | absolute paths, `cd` to a home or shared drive, `global root` set to a machine path | `ssc install`, `net install`, `copy "http…"`, `import … using "http…"` | `shell`, `!`, `winexec` |
| R | `unlink`, `file.remove`, `file.rename` outward | `setwd()` to an absolute path, `here()` roots outside the copy | `install.packages`, `download.file`, `curl`, `httr`, `renv::restore()` | `system()`, `system2()` |
| Python | `os.remove`, `shutil.rmtree`, `Path.unlink` | absolute paths, `os.chdir` | `pip`, `requests`, `urllib`, `wget` | `subprocess`, `os.system` |

Neutralize in the copy (rule D in the protocol): redirect the path, comment
the line, or set the root global to the copy. Save the diff as
`ew/log/<script>.patch` and cite it in the finding.

## Batch invocations

**Stata.** Find the binary: `which stata-mp stata-se stata`; on macOS also
`/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp` (and `StataSE`,
`Stata`). Run from the script's own directory so relative paths resolve:

```bash
cd "<copy>/code" && "<stata>" -b do master.do
```

`-b` writes `master.log` beside the script. Stata's exit status is not
reliable; grep the log for `^r\([0-9]+\);` and for `no such file`,
`not found`, `invalid syntax`. `set more off` is implied by `-b`. A
`log using` inside the script writes a second log; capture both. Copy the
logs to `ew/log/` and redact any `list`, `browse`, or `tab` output that
shows individual rows before committing.

**R.** `cd "<copy>/code" && Rscript master.R > "<run>/ew/log/master.R.log" 2>&1`.
If there is a `renv.lock` and `HOST.md` allows installs, `renv::restore()`
first and record the versions; otherwise run with what is installed and
record `sessionInfo()` in the log.

**Python.** Use a virtual environment under `ew-local/venv` so nothing is
installed system-wide. `pip install -r requirements.txt` only if allowed;
record the resolved versions (`pip freeze > ew/log/pip-freeze.txt`).

**Long jobs.** Run in the background and tail the log; note the start and
end in `STEPLOG.md`.

## Reading output into reproduced.csv

Take values from the pipeline's own output files (the `.tex`, `.csv`,
`.xlsx`, or log the authors' script writes), not from re-typing a screen.
Keep full precision; `compare.py` rounds to the paper's printed digits. If
the output file applies rounding or formatting (`esttab` with `b(3)`), say
so; the comparison then uses the printed digits.

## Writing your own scripts for Part B items

- One script per item, in the language the analysis file is easiest to read
  in. Stata `.dta` can be read from Python with `pandas.read_stata` (check
  value labels and dates) and from R with `haven`.
- Start by loading the authors' analysis file and asserting the N the paper
  reports for that sample. If it differs, that is the first line of the
  item's Observations.
- Reproduce the paper's own specification first (the same controls, fixed
  effects, and clustering), confirm you match the paper's coefficient, and
  only then vary what the item asks you to vary. An item result that does
  not start from a matching baseline is not interpretable.
- Randomization inference: enumerate assignments within blocks exactly when
  the count is manageable (product over blocks of C(sections, treated));
  otherwise draw with a recorded seed. The statistic is whatever the item
  specifies; default to the t-statistic from the paper's specification. Report
  the number of assignments and the share with |t| at or above the observed.
- Wild cluster bootstrap: Rademacher weights (Webb weights when clusters < 12),
  9,999 replications, seed recorded; `boottest` in Stata, `fwildclusterboot`
  in R, or a short hand-rolled version in Python with the formula in the
  script's header.
- Apply the disclosure rules inside the script, before any write.

## Comparing numbers

- Printed digits decide the tolerance: a printed `-2.88` matches a computed
  `-2.8849`; a printed `0.02` matches `0.0151` through `0.0249` and, by the
  one-unit rule, `0.025` through `0.034` as well, with a note.
- Standard errors in parentheses under coefficients; stars are a separate
  field, compared as printed.
- When the paper's units are control-group SDs, recompute the SD the way
  the paper describes (control group, that sample) and show the division.
