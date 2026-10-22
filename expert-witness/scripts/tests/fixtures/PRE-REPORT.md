# Pre-report: Tutoring and Grades in a Fixture Trial

A short pre-report used by the tests in scripts/tests/run_tests.py. It follows
assets/PRE-REPORT-TEMPLATE.md; item B2 uses the plain-hyphen heading form on purpose.

## Header

- **Paper:** A. Author and B. Author, *Tutoring and Grades*, working paper, 2026.
- **Model and effort requested:** claude-opus-5-5; effort high.

## Part A — Reproduction

### A1 — Table 3, both panels

**Tier:** 1
**Exhibits:** Table 3 (p. 41), Panels A and B, with and without controls.
**Cells:** all.
**Notes:** Standard errors are clustered by section; confirm the cluster count.

## Part B — Requested analyses

### B1 — Randomization inference for Table 3

**Tier:** 1
**Question:** What are the randomization-inference p-values for the six
outcomes in Table 3, and does the footnote's procedure produce them?
**Paper's statement at issue:** "Our conclusions are robust to this approach." (p. 19)
**Specification:** Enumerate assignments within blocks:
- hold the number of treated units per block fixed;
- re-estimate Equation (1) for each assignment.

```stata
* the paper's specification, for reference
# not a heading: this line is inside a code block
reg y treat i.block, cluster(section)
```
**Output:** A table of p-values with the observed t-statistic beside each.
**Disclosure:** none beyond the standing rules.
**Resolution:** If the p-values are below 0.05, the footnote's statement is supported in
the sense that the gap is rare under re-randomization; if they are above, it is not.
Either is reported without characterization.

### B2 - Activities available per section

**Tier:** 2
**Question:** How many gradable activities did each arm's sections make available?

- (a) as a distribution across sections;
- (b) as a share of the activities the participation metric counts.

**Paper's statement at issue:** "Total participation depends on the activities required by the instructor." (p. 13)
**Specification:** Count published activities per section from the LMS export.
**Output:** Quantiles by arm.
**Disclosure:** Sections only as distributions.
**Resolution:** If the arms differ, the statement is supported in that sense; if not, it is
not. Either is reported without characterization.

## Part C — Documentation

### C1 — Outcome construction

**Tier:** 1
**Question:** How is each outcome built from the exports?
**Specification:** For each outcome: the export file, the field, and the transformation in
code (file and line). Quote code; do not quote data.
**Output:** One table, one row per outcome.

## Part D — Restrictions on the witness

- Do not open the chat corpus.
