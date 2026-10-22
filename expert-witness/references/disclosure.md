# Disclosure: what may leave the host's machine

The data are about students and instructors who consented to a study, under
terms (FERPA, an IRB protocol, a data-use agreement) that the witness did not
sign and cannot waive. The report is read by people outside the study team.
These rules decide what goes in it. When a rule and a requested item
conflict, the rule wins and the item is reported as
`ANSWERED-WITH-RESTRICTIONS` (coarser) or `NOT-ANSWERABLE` (rule named).

The pre-report sets defaults; `HOST.md` may tighten them and may not loosen
them below the pre-report's floor. Where the two differ, the stricter
applies, point by point.

## Rules

1. **Aggregates only.** No row about a student, an instructor, or a section
   leaves the machine, in any file, including logs. Logs from the authors'
   pipeline often print observations; redact before committing (the checker
   helps; your eyes finish the job).
2. **Minimum cell count.** Default 10 observations behind any reported
   count, mean, share, or regression subgroup. A regression coefficient is
   fine when the sample behind it meets the minimum; a subgroup estimate
   reports its N. Suppressed cells print `<10`, never a blank.
3. **Complementary suppression.** If a cell is suppressed and its margin is
   reported, suppress a second cell in the same row or column so the first
   cannot be recovered by subtraction.
4. **Sections and instructors.** Thirty-odd instructors are identifiable
   from a course number and a term. So: no course numbers or titles beyond
   the labels the paper itself prints (its block labels are fine); section-
   level quantities only as distributions (bins, quantiles over at least five
   units, counts of sections meeting a condition), never as a list of
   per-section values, unless `HOST.md` explicitly permits per-section rows
   under random labels. If it does, generate the labels with a seed, keep
   the map in `ew-local/section-map.csv`, and never commit the map.
   Instructor demographics are reported only at the level the paper already
   reports them.
5. **Quasi-identifiers.** No cross-tabulation that combines three or more of:
   race/ethnicity, gender, first-generation status, international status,
   class year, section. Two-way tables are fine when every cell meets the
   minimum.
6. **Text.** No content from chat logs, free-text survey answers, emails, or
   messages, in any length, including single words. Survey item wording and
   response categories are instrument text and are fine.
7. **Dates.** Semester weeks are fine. Exact dates of an individual's actions
   are not. Export dates and activation dates are fine at the section level
   only if rule 4 allows section rows; otherwise as a distribution.
8. **Identifiers.** No names, emails, UIDs, student numbers, IP addresses, or
   any string the host's sensitive-terms list contains. This applies to the
   interventions log too: the host's words are recorded verbatim for
   accountability, not for identification, so a personal name or an
   identifier inside a host statement is replaced with `[name]` or `[id]`
   and the entry says "redacted by the witness". Nothing else in the entry
   is changed.
9. **Already public.** A number the paper prints may be repeated. That the
   paper printed it does not make the row behind it reportable.
10. **Small samples in heterogeneity.** A subgroup with fewer than the
    minimum in either arm is reported as `<10` for the subgroup N and the
    estimate is omitted.

## Mechanics

- Apply suppression in the script that writes the output, not afterwards by
  hand, so the committed file was never unsafe.
- Every committed output under `ew/items/<ID>/` is a table with column
  headers; the checker flags integer cells under the minimum in columns whose
  header looks like a count (`n`, `N`, `count`, `students`, `obs`,
  `sections`). Confirm each flag: a coefficient of 7 is not a count; a
  section count of 3 may be fine (sections are not people) and still needs
  rule 4's distribution form.
- `ew-local/sensitive-terms.txt`: one term per line, supplied by the host
  (instructor names, course titles, internal system names). The checker
  matches case-insensitively. The file is gitignored and listed in
  `INTAKE.md` only by its hash.
- The checker (`scripts/disclosure_check.py`) scans every non-binary file
  you commit (including `.log`, `.smcl`, and `.patch` files) and exits
  non-zero on any hit; the pre-commit hook blocks the commit. False
  positives go in `ew/disclosure/allow.txt`, one per line as
  `rule:pattern|reason`, so that an allowance for one rule never silences
  another. "Table 3" is not an instructor; "0.37" is not a count; a file
  size in `census.json` is not an ID. The checker already exempts digit
  runs inside long hexadecimal hashes.
- Quoted sentences that come from the paper or the pre-report (the
  "Bearing on the paper's statement" lines, the verbatim Questions) are
  public text, not data. Run the checker with `--pre-report PRE-REPORT.md`
  and it exempts any quoted span that also appears there. A quoted span of
  more than twelve words that appears nowhere in the pre-report is flagged,
  and should be: the only other source of a sentence in quotation marks is
  the data. Shorter quoted spans are below the checker's threshold (a
  variable name in quotes is not a quotation), so rule 6 for those is
  yours to keep by eye: a chat phrase of five words is still chat text.
- The `listing` rule fires on anything that looks like rows of a dataset,
  which includes some ordinary Stata output (`tab`, echoed loops). It is a
  prompt to look, not a verdict; clear a false positive with a
  `listing:` allow entry whose reason names what the lines are.

## The whole-report checklist (phase 5)

Answer each in `ew/disclosure/CHECK.md`, with the file and line for any
"no":

1. Does any committed file contain a row about one person or one section?
2. Does any count, mean, or share rest on fewer than the minimum?
3. Where a cell is suppressed, could it be recovered from a margin?
4. Does any file name a course beyond the paper's own labels, or an
   instructor by rank, department, or any attribute combination?
5. Does any file quote a chat, a free-text answer, or a message?
6. Does any log under `ew/log/` print observations, names, or IDs?
7. Does any script under `ew/items/` embed a value from the data as a
   literal (a name, an ID, a date of an individual action)?
8. Are the section-label map and sensitive-terms file absent from the
   repository and listed in `.gitignore`?
9. Does the report print any date that locates one person's action?
10. Did the checker pass on the whole tree with an allow-list you can defend
    line by line?

## Examples

Allowed: "In the exact-match sample, 3 of 10 control sections and 0 of 12
treated sections had more than 50 gradable activities." Allowed: a 5×6
cross-tab of grade band by letter grade with every cell ≥ 10. Allowed:
"Treated respondents: n = 141; control respondents: n = 203."

Not allowed: a table with one row per section, however labeled, unless
`HOST.md` says so. Not allowed: "the Humanities #2 treated section's
instructor, a lecturer". Not allowed: "one student wrote that the tutor
…". Not allowed: a log excerpt showing `list in 1/5`.
