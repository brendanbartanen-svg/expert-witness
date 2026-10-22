# REPORT.md template

`scripts/init_report.py PRE-REPORT.md` generates this skeleton with one
section per item, copying each item's title and question verbatim. Fill
every field; a field that does not apply says `none`, never nothing.

```markdown
# Expert Witness Report: {paper title}

**Status:** COMPLETE | PARTIAL (outstanding: B7, B9) | STOPPED BY HOST (phase 4, item B5)

**Pre-report:** PRE-REPORT.md @ {commit} (blob {hash})

**Host declaration:** HOST.md @ {commit} (blob {hash})

**Model:** {actual model id} (requested: {model}); effort: {actual} (requested: {effort})

**Run:** {start} – {end}; phases: census {m}m, read {m}m, reproduce {m}m, items {m}m, review {m}m

**Package:** {dir}; {N} files; census {hash of census.json}

**Disclosure terms in force:** min cell {n}; section rows {permitted under random labels | not permitted}; {other}

## Summary of findings

| Item | Tier | Finding | Result in one line |
|---|---|---|---|
| A1 | 1 | REPRODUCED-WITHIN-TOLERANCE | 24 of 24 cells within one unit of the last printed digit |
| B1 | 1 | ANSWERED | RI p-values: … |
| … | | | |

## Part A — Reproduction

### A1 — {title}

**Exhibits:** {tables/figures}

**Source:** {script → output file}, run from {raw | intermediate file `…`}

**Finding:** REPRODUCED | REPRODUCED-WITHIN-TOLERANCE | DIFFERS | COULD-NOT-RUN | NOT-APPLICABLE

**Comparison:** ew/reproduction/COMPARE.md#{anchor}; {k} of {n} cells within tolerance; largest difference {…} at {cell}

**Observations:** {anything encountered that bears on this exhibit: exclusions not described, constructions that differ from the text, hand steps} | none

**Files:** ew/log/{…}

## Part B — Requested analyses

### B1 — {title}

**Question (from the pre-report, verbatim):**
> {the item's Question field}

**Specification followed:** {the literal reading; alternative reading, if reported}

**What was done:** {script path; inputs with hashes; definitions used; seeds; software}

**Result:**

{table or numbers, disclosure applied}

**Finding:** ANSWERED | ANSWERED-WITH-RESTRICTIONS | NOT-ANSWERABLE | NOT-ATTEMPTED

**Plain result:** {one sentence, true whichever way the parties hoped it would come out}

**Bearing on the paper's statement:** The pre-report cites: "{quoted sentence}" (p. {n}). The requested quantity {is | is not} consistent with it in the following sense: {…}.

**Observations:** {…} | none

**Disclosure notes:** {suppressions applied; rule numbers} | none

**Files:** ew/items/B1/{script}, ew/items/B1/{log}, ew/items/B1/{outputs}

## Part C — Documentation

### C1 — {title}

**Question (verbatim):**
> …

**Answer:** {description, with file and line references into the package}

**Finding:** ANSWERED | ANSWERED-WITH-RESTRICTIONS | NOT-ANSWERABLE | NOT-ATTEMPTED

**Files:** …

## Noted, outside scope

- {one line each; no numbers; no conclusions} | none

## Interventions

{count} recorded; full log in ew/INTERVENTIONS.md. {one line each: timestamp, kind, followed/declined}

## Environment

{from CENSUS.md: OS, software and versions, packages installed during the run and by whose permission}

## Method notes

{anything general: how control-SD units were computed; the RI procedure and the number of assignments enumerated; clustering; the tolerance rule; the labeling scheme}
```

Fields are separated by blank lines so that each renders as its own
paragraph on GitHub; a Result table stands between blank lines like any
other block.

Three habits that keep the template honest:

- The "Plain result" sentence is written before the "Bearing" line, and
  without looking at the paper's sentence. Then compare.
- A `DIFFERS` or an unfavorable result gets the same number of words as a
  `REPRODUCED` or a favorable one. If one is longer, the other is
  incomplete.
- Every number in the Result block appears in a committed file under
  `ew/items/<ID>/`. If it does not, it is not in the report.
