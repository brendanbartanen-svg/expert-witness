# Pre-report: The Effects of Course-Integrated AI Tutoring on Student Performance and Engagement: A Randomized University Trial

A pre-report is the report with the answers blank. It fixes the questions
before anyone has seen the data, so that the answers cannot shape them.
The witness copies each item's title and question into `REPORT.md`
verbatim and fills in the rest.

## Header

- **Paper:** Jing Liu, Tracy Sweet, Marty Haoyuan Chen, Jonathan Engelberg,
  Martyn Clark, Axel Persaud, Alia Lancaster, Jeffrey Hollingsworth,
  Jennifer King Rice, and Megan Masters. *The Effects of Course-Integrated AI
  Tutoring on Student Performance and Engagement: A Randomized University
  Trial.* EdWorkingPaper No. 26-1598, Annenberg Institute at Brown
  University; manuscript dated September 29, 2026 ("VERSION: October 2026").
- **Artifact under examination:** `ai26-1598.pdf`; SHA-256
  `99b651b7369cbc9ba822f958aff5676f6002f39ee0d5d5e93ccdb34c6a792c07`.
  Page numbers below are the paper's **printed** page numbers (PDF page
  minus 2). If the authors have since revised the paper, the items still
  refer to this version; the witness notes where a later version differs.
- **Requester:** Brendan Bartanen, University of Virginia; role: reader. Not an editor or referee of this paper.
- **Requester's declarations:** I published a critique of this paper on
  October 15, 2026 ("AI tutoring lowers student performance and
  engagement. Or does it?") and have corresponded with the lead author
  about it. I have no financial or professional interest in the result. I
  have told the authors, and repeat here, that I will write a follow-up
  consistent with whatever this report shows, in either direction. The
  items below are the questions on which my critique and the authors'
  replies disagree, written so that either outcome is reportable.
- **Host:** the authors, in their own environment, under their IRB protocol
  (K-2768) and data-use terms; or a third-party environment the authors and
  an editor agree on. See `HOST.md`.
- **Repository:** to be created by the host or an editor; read access for
  the authors, the handling editor and referees if the paper is under
  review, and the requester.
- **Model and effort requested:** Claude Fable 5.1 (`claude-fable-5-1`) at
  the highest available effort setting. Acceptable substitute: Claude Opus
  5.5 (`claude-opus-5-5`) at the highest effort. The report records what
  was used.
- **Tiers:** Tier 1 is the set of items that bear directly on the three
  claims in the abstract. The host may release `report-v1` after tier 1 and
  `report-v2` after tiers 2 and 3.
- **Date fixed:** the date this file is first committed to the repository.

## Scope

The paper reports that access to a course-integrated GenAI assistant reduced
final grades by 0.37 SD and LMS participation by 0.90 SD in the exact-match
sample, with larger grade losses for first-generation students, and
conjectures that the effects ran through a change in the classroom AI
environment rather than through use of the tool, which about 15% of treated
students used. The requester has argued publicly that the grade effect
depends on which of six estimates is read, that the participation measure
reflects instructor-assigned activity rather than student behavior, that
the first-generation result is one of many unadjusted interactions, and
that the mechanism is untested. The paper's own text supplies the
counterpoints: the exact-match letter-grade effect is also negative and
significant (p. 19); footnote 5 states that randomization inference
supports the conclusions; the homework-assigned difference is not
significant in the full sample (Table 1); and the survey evidence on
instructor encouragement is read as support for the mechanism (pp. 23–24).
Each of these is a question about what the data show, and each item below
is written so that the data can answer it either way.

The witness answers the items below, reports in both directions with equal
care, characterizes no one's motives, rates nothing, and reports anything
encountered that bears on an item under that item's Observations. Matters
outside the items are listed in one line each without analysis.

## Disclosure rules for this run

- Minimum cell count: 10 students. Suppressed cells print `<10`.
- Section-level rows under random labels: **not permitted** unless `HOST.md`
  permits them. Section-level quantities are reported as distributions
  (bins, quantiles over at least five sections, counts of sections meeting a
  condition) and as block-by-arm means only where `HOST.md` permits.
- Course identification: the block labels of Table A1 (A–P; "STEM #3",
  "Soc Sci #7") only. No course numbers, titles, or departments.
- Instructor attributes: only at the level Table 1 and Table A2 already
  report.
- Text from VSA chats, free-text survey answers, emails, or ELMS messages:
  none, of any length. Survey item wording and response categories may be
  quoted.
- Student-level data are never written to any file under `ew/`.
- `HOST.md` may tighten any of these.

## Part A — Reproduction

Run the authors' code as shipped, from the analysis file at minimum and from
the raw ELMS and registrar exports if the package includes them, and compare
its output with the printed exhibits. Report, for each, whether the
reproduction started from raw data or from an intermediate file.

### A1 — Table 3, both panels, with and without controls

**Tier:** 1
**Exhibits:** Table 3 (p. 41): 24 coefficients, 24 standard errors, the
control SDs, and the observation counts.
**Cells:** all.
**Notes:** Confirm the sample sizes (2,379 / 2,362 full; 1,353 / 1,343
exact-match) and the control-group SDs (10.10, 0.78, 10.18, 1559.40, 15.29,
25.36; 11.09, 0.86, 11.36, 1969.14, 14.16, 29.25). Confirm that standard
errors are clustered at the course-section level with 34 clusters (full)
and 22 (exact-match), as the table note states, and report the number of
clusters the code actually uses.

### A2 — Table 2, summary statistics by use status

**Tier:** 1
**Exhibits:** Table 2 (p. 40), both samples, all rows, including the
observation counts 1,227 / 172 / 980 and 612 / 97 / 644.
**Cells:** all.
**Notes:** Report the definition of "used VSA" (at least one interaction, or
at least one session) that the code applies.

### A3 — Balance tables and homework submission

**Tier:** 2
**Exhibits:** Table 1 (p. 39), Table A2 (p. 51), Table A3 (p. 52).
**Cells:** all, including the course-and-instructor rows.
**Notes:** For the course-and-instructor rows, report how the printed means
are computed (section-level means, student-weighted means, or something
else), since 1,227 students over 17 control sections is 72.2 per section
while the table prints 125.8.

### A4 — Heterogeneity tables

**Tier:** 2
**Exhibits:** Table 4 (p. 42) and Table A4 (p. 53).
**Cells:** all interaction coefficients and standard errors; the
first-generation rows in full.
**Notes:** Report the observation counts for the high-school-GPA panel
(1,967 / 1,952; 1,119 / 1,111) and what accounts for the difference from
the other panels.

### A5 — Discipline tables

**Tier:** 2
**Exhibits:** Table 5 (p. 43) and Table A5 (p. 54).
**Cells:** all.
**Notes:** The text (p. 22) says the humanities final-grade and letter-grade
effects are significant at the 1% level; Table 5 marks them at 5%. Report
the p-values the code produces.

### A6 — Distribution figures

**Tier:** 1
**Exhibits:** Figure 2 panels (a) and (f) (p. 35); Figure 3 panels (a) and
(f) (p. 36).
**Cells:** regenerate as binned counts by arm: final grade in bins of 5
points from 0 to 100 (with scores above 100 in a top bin); total
participation in bins of 10 from 0 to 120 (top bin open). Report bin counts
and shares by arm for each sample; bins with fewer than 10 students print
`<10`.
**Notes:** These binned tables replace the kernel densities for the
purposes of items B2 and B3; the witness need not reproduce the density
plots themselves.

### A7 — Instrumental-variable and complier exhibits

**Tier:** 3
**Exhibits:** Table A6 (p. 55); Figure 4 (p. 37) and Figure A5 (p. 48) as
tables of coefficients and confidence intervals.
**Cells:** all.
**Notes:** Confirm the first-stage coefficients (0.15, 0.13) and F-statistics
(50.5, 16.5).

## Part B — Requested analyses

### B1 — Randomization inference for Table 3

**Tier:** 1
**Question:** What are the randomization-inference p-values for each of the
six outcomes in Table 3, in both samples, with and without controls, and
does the procedure described in footnote 5 produce them?
**Paper's statement at issue:** "We therefore also conducted randomization
inference, re-randomizing treatment across instructors within randomization
block while holding the number of treated instructors per randomization
block fixed, and comparing the observed t-statistics with their distribution
across re-randomizations. Our conclusions are robust to this approach."
(p. 19, fn. 5)
**Specification:** Using the analysis file and the paper's Equation (1)
specification: (a) identify the unit actually randomized (instructor or
section) and the block membership of each unit; (b) enumerate every
assignment that holds the number of treated units per block fixed (report
the count per sample; if it exceeds 100,000, draw 10,000 with seed 26159801
and say so); (c) for each assignment, re-estimate Equation (1) with
course-section clustering and record the t-statistic on Treated; (d) the
two-sided p-value is the share of assignments with |t| at or above the
observed |t|. Do this for all six outcomes × two samples × with and without
controls. Separately, if the package contains the authors' own
randomization-inference code, run it as shipped and report its p-values
and how its procedure differs from (a)–(d), if at all.
**Output:** A 24-cell table of p-values with the observed t-statistic beside
each; the number of assignments enumerated or drawn per sample; the
authors' own RI p-values if the code exists.
**Disclosure:** none beyond the standing rules.
**Resolution:** If the RI p-values for the participation outcomes (columns
4–6) are below 0.05, the footnote's statement is supported for those
columns in the sense that the observed gap is rare under re-randomization
of the same sections, which bears on the "unlucky draw" explanation (see
B2). If the RI p-value for exact-match final grade (Panel B, column 1) is
below 0.05, the abstract's 0.37 SD estimate survives this inference; if it
is above, it does not. If the RI p-value for the exact-match letter grade
(Panel B, column 2) is far above the cluster-robust p < 0.01, item B4's
concern about that standard error is supported; if it is also below 0.01,
it is not. Either is reported without characterization.

### B2 — Activities available per section, and participation as a share

**Tier:** 1
**Question:** How many gradable ELMS activities did each section make
available during Fall 2025, by arm; does the treatment–control gap in total
participation remain when participation is expressed as a share of
available activities or when activities available is controlled; and is the
difference in activities available between arms itself unusual under
re-randomization?
**Paper's statement at issue:** "The contrast is particularly pronounced for
total participation: treatment students' activity is concentrated at
relatively low levels, whereas the control distribution has substantially
more mass at higher participation levels. The patterns suggest that VSA
access was associated with lower engagement with the existing learning
management system." (p. 18); and "Total participation depends on the
activities required by the instructor in ELMS." (p. 13)
**Specification:** (a) State the ELMS definition of a "participation" used
to build total participation (the export field and the activity types it
counts). (b) For each section, count the activities of those types that
were published to students during the semester (assignments, quizzes,
graded discussions, and any other type the participation metric counts),
from the ELMS data the package or the host's ELMS office holds; if the
count cannot be built, say exactly what is missing. (c) Report, by arm and
sample: mean, SD, minimum, maximum, and the 25th/50th/75th percentiles of
activities available across sections; the number of sections with more than
50 available; the number with more than 30. (d) Re-estimate Equation (1)
for total participation with activities available added as a covariate, and
for the share participations ÷ activities available (students whose section
has zero available are excluded; report their number by arm, `<10` if
fewer). (e) Randomization-inference p-values (B1's procedure) for the two
estimates in (d). (f) Randomization-inference p-value treating activities
available as the outcome (section-level, within block). (g) State whether
"HW Assigned" and "HW Possible Score" in Tables 1 and A2 are measured for
Fall 2025 or an earlier term, and report their RI p-values as in (f).
(h) Report the control and treated distributions of total participation
from A6 beside the distribution of activities available, in the same bins.
**Output:** The statistics in (c) as a table; the four estimates in (d) with
cluster-robust SEs, control-SD units, and RI p-values; the p-values in (f)
and (g); the binned distributions in (h).
**Disclosure:** Minimum and maximum of activities available are single
sections' values; report them only if `HOST.md` permits section-level
values, otherwise report the 10th and 90th percentiles instead.
**Resolution:** If the estimate on the share measure, or on the count with
activities available controlled, remains negative with an RI p-value below
0.05 and a magnitude of at least half the paper's 0.90 SD, the paper's
reading of total participation as a measure of student engagement is
supported in the sense that the gap is not accounted for by differences in
what was offered. If the estimate falls to within 0.2 SD of zero or its RI
p-value exceeds 0.10, the 0.90 SD is accounted for, in whole or in large
part, by differences in activities available; whether those differences
are chance or an effect of treatment on instructors is then what (f) and
(g) speak to: an RI p-value below 0.05 in (f) means the arms differ in
activities available by more than re-randomization produces, which is
consistent with treatment having changed what instructors assigned; a
p-value above 0.10 means the difference is within what chance produces.
Because activities available may itself respond to treatment, (d) is read
together with (f), and the report presents them side by side. Intermediate
results are reported as such.

### B3 — Construction and completeness of the ELMS final grade

**Tier:** 1
**Question:** Which ELMS gradebook field is the "final grade" outcome, when
was it exported relative to grade finalization, how complete were the
gradebooks at export, and how do ELMS final grades below 60 relate to the
letter grade of record, by arm?
**Paper's statement at issue:** "final grades provide a more granular, and
arguably more objective, measure of course performance than course letter
grade and may therefore capture changes that do not translate into
differences in letter grade, particularly when the latter reflects discrete
letter-grade thresholds." (p. 19); and "in the model that included control
variables, course grades were 4.12 points lower in the treatment condition,
which is equivalent to 0.37 standard deviations." (p. 19)
**Specification:** (a) Name the export field (for example, Canvas "current
score", "final score", "unposted current score", "unposted final score",
or "override score") and state how that field treats unsubmitted
assignments (counted as zero or excluded) and whether it reflects
instructor overrides. (b) State the export date(s) and the date final
letter grades were due to the registrar; report, by arm, the number of
sections whose gradebook was exported before grades were finalized, if this
can be determined. (c) By arm and sample: the share of students with ELMS
final grade below 60, below 50, and equal to 0; and the share with letter
grade of record F, D, or W/incomplete/other. (d) A cross-tabulation, by arm,
of ELMS final-grade band (<50, 50–59, 60–69, 70–79, 80–89, 90–100, >100) by
letter grade (A, B, C, D, F, other), cells below 10 suppressed with
complementary suppression. (e) The number of sections, by arm, in which
more than 5% of students have ELMS final grade below 60; for students in
those sections, the share with letter grade F (suppressed if fewer than
10 students). (f) Re-estimate Table 3, columns 1 and 2, both panels, with
controls, (i) excluding students with ELMS final grade below 60 and letter
grade of record C or better, reporting the number excluded by arm, and
(ii) replacing the ELMS final grade with the letter grade's midpoint on a
0–100 scale (A = 95, B = 85, C = 75, D = 65, F = 50) as a check on the scale
conversion. (g) The implied letter-grade change per ELMS point in the
control group: the slope of letter grade on ELMS final grade among control
students, by sample, and the letter-grade effect this slope implies for the
paper's final-grade coefficient, beside the paper's actual letter-grade
coefficient.
**Output:** (a) and (b) as a description; (c)–(g) as tables.
**Disclosure:** (d) and (e) require complementary suppression; (b) is
reported as counts of sections by arm, not dates by section.
**Resolution:** If the field excludes unsubmitted work and gradebooks were
complete at export, and the cross-tab in (d) shows students with ELMS
grades below 60 holding F or D letter grades at similar rates in both arms,
the paper's final-grade outcome is a complete record of course performance
and the 0.37 SD stands as a measure of that record. If the field counts
unsubmitted work as zero, or gradebooks in some treated sections were
incomplete at export, or (d) shows treated students with ELMS grades below
60 holding C or better at a higher rate than controls, then part of the
final-grade gap reflects the state of the gradebook rather than performance,
in the amount (f)(i) shows. If (g)'s implied letter-grade effect is close to
the actual letter-grade coefficient, the two measures move together; if the
actual is a fraction of the implied, they do not, and the paper's threshold
explanation does not account for the difference. Either is reported without
characterization.

### B4 — Precision of the exact-match letter-grade estimate

**Tier:** 2
**Question:** Is the standard error of 0.02 on the exact-match letter-grade
estimate (Table 3, Panel B, column 2, with controls) reproduced under
alternative inference, and what accounts for its size relative to the other
columns?
**Paper's statement at issue:** "Similarly, course letter grades in GPA scale
were lower by 0.11 points (0.13 SDs)." (p. 19), with the table entry
−0.11*** (0.02).
**Specification:** For Table 3, Panel B, column 2, with and without
controls: (a) the coefficient and cluster-robust SE as in the paper, to four
decimals; (b) the SE clustered by instructor rather than section; (c) a wild
cluster bootstrap p-value (Webb weights, 9,999 replications, seed 26159802)
clustered by section; (d) the RI p-value from B1; (e) the number of
clusters, the number of blocks, and the SD across sections of the
block-demeaned, covariate-residualized section mean of letter grade; (f)
the same quantities for column 1 (final grade) for comparison; (g) the ratio
SE ÷ control SD for each of the six columns, with and without controls.
Also: (h) the number of students with a final grade but no letter grade of
record (2,379 − 2,362; 1,353 − 1,343), by arm, and the recorded reason
categories as counts.
**Output:** One table with rows (a)–(g) for columns 1 and 2; a line for (h).
**Disclosure:** (h) by arm only; `<10` if fewer.
**Resolution:** If the wild-bootstrap and RI p-values for column 2 are
below 0.05, the estimate's significance is supported under inference that
does not rely on the cluster-robust SE. If they are above 0.10, the printed
*** overstates the precision of that cell. The ratio table in (g) reports
whether column 2's precision is in line with the others; the witness
reports the numbers and the between-section SD in (e) without further
interpretation.

### B5 — Analyze as randomized: excluded instructors, late joiners, opt-outs

**Tier:** 1
**Question:** What was the full randomized sample, which units were removed
or added after randomization and when, and what are the Table 3 estimates
when every randomized instructor is retained in the arm assigned?
**Paper's statement at issue:** "As our experiment aims to evaluate how VSA
access affects student outcomes rather than instructors' uptake, we removed
instructors who did not activate the VSA from our sample (n = 3
instructors)." (p. 10); and "we estimate the intention-to-treat (ITT) effects
of VSA access." (p. 16)
**Specification:** (a) From the randomization record, list by block label
(Table A1) and arm: the number of instructors randomized, the number
retained, the number removed with the reason category (did not activate;
withdrew; other), the number added after the semester began with the
semester week of addition, and the number of students in each category.
(b) Re-estimate Table 3 (both panels, with controls) retaining the three
non-activating treated instructors' sections, coded as assigned to
treatment, if their students' outcome data exist; if the data were never
collected, say so and report what would be needed. (c) For each treated
section, the semester week in which the VSA was activated; report the
distribution (number of sections activated by week 2, by week 5, by week 8,
later), and, if page views and active days are datable, re-estimate columns
4 and 5 restricted to the weeks after the latest activation in each block.
(d) The number of students who opted out of the study and the number
excluded as under 18, by arm.
**Output:** (a) as a table by block and arm; (b) as a 12-cell table beside
the paper's; (c) as a distribution and two re-estimates; (d) as counts.
**Disclosure:** (a) uses block labels; where a block has fewer than 10
students in a category, print `<10`. (c) reports the distribution of
activation weeks, not per-section dates.
**Resolution:** If (b) is within 0.1 SD of the paper's estimates, the
removal of the three instructors did not materially change the results. If
(b) differs by more than that, the estimates reported as ITT depend on a
post-randomization exclusion in the amount shown. If the data for (b) were
never collected, the ITT-as-randomized estimate cannot be computed and the
report says so. (c) reports whether the engagement effects hold in the
post-activation window; either outcome is reported as is.

### B6 — Survey evidence on the mechanism

**Tier:** 1
**Question:** By arm, what did students report about their general use of
GenAI during the semester, about office hours, and about instructor
encouragement; how did survey respondents differ from non-respondents in
each arm; and what does the instructor survey show about integration of the
tool?
**Paper's statement at issue:** "Thus, the intervention likely evaluates an
impact of broader AI use induced by introducing the VSA and not just the
isolated effect of individual VSA use." (p. 29); "The survey assessed
students' general use of GenAI across the semester, perceptions of
student–instructor interactions (e.g., student questions for instructors;
office hours attendance) …" (p. 13); "We do not observe their use of these
alternatives" (p. 17).
**Specification:** (a) Response rates by arm, both samples, and the
block-adjusted difference (the paper reports 4.3 points, p < 0.01). (b) Among
respondents and non-respondents within each arm: means of the Table 1
covariates and of final grade and total participation, as a four-column
table. (c) The exact wording and response categories of every student
survey item about general GenAI use during the semester (frequency, tools
used, purposes); the distribution of each by arm among respondents; and the
block-adjusted difference with a cluster-robust SE. (d) The same for the
office-hours item(s) and for the instructor-encouragement item in Figure 5.
(e) For the items in (c): the distribution among treated respondents by VSA
use status (used / did not use). (f) The "office hours check-ins" data
collection shown in Figure A4: what was collected, from whom, and whether
it yields a by-arm count or rate; if so, report it. (g) The instructor
survey: the number of respondents by arm; for treated respondents, the
counts for the items on monitoring VSA use, demonstrating the tool, and
incorporating it into assignments (p. 15); the items on AI policy for
control respondents, if any.
**Output:** Tables for (a)–(e) and (g); (f) as a description plus a table if
available.
**Disclosure:** All distributions with cells below 10 suppressed; (e) only if
the treated-user respondent count is at least 10 in each sample; no
free-text responses; item wordings may be quoted.
**Resolution:** If (c) shows treated respondents reporting more general
GenAI use than control respondents, the paper's conjecture that the
intervention changed broader AI use has support in the authors' own survey
data, subject to the response-rate caveat the paper states. If (c) shows no
difference or less use, the conjecture has no support in those data. (d)
reports whether office-hours attendance differed by arm, which the paper
does not currently report; (b) reports how selective the respondent sample
is in each arm. Either outcome is reported without characterization.

### B7 — Section-level structure of the outcomes

**Tier:** 2
**Question:** How much of the variation in final grade and total
participation lies between sections within block, by arm, and how many
sections per arm account for the upper tail of the control participation
distribution?
**Paper's statement at issue:** "As students in these blocks went through
largely the same curricula, assessments, and grading scales, the exact-match
sample holds course content fixed and helps isolate the impact of VSA from
other extraneous course-level factors." (p. 12); and "sections may still
differ in grading and opportunities for platform participation." (p. 29)
**Specification:** For each outcome in Table 3, both samples: (a) a variance
decomposition of the block-demeaned outcome into between-section and
within-section components, by arm; (b) the SD across sections of section
mean outcomes within block, by arm; (c) the number of sections, by arm,
whose mean total participation exceeds 40, and the share of control
students above 50 participations who are in those sections; (d) if
`HOST.md` permits, block-by-arm section means for the six outcomes and for
activities available (B2) using Table A1's block labels; otherwise the
distributions in (a)–(c) only.
**Output:** Tables.
**Disclosure:** (d) only under `HOST.md` permission; (c) reports counts of
sections and shares of students, not section identities.
**Resolution:** Reported descriptively. If the upper tail of control
participation comes from a small number of sections, the 0.90 SD gap is
concentrated in those sections' comparisons; if the between-section SD is
similar across arms and the tail is spread across many sections, it is not.

### B8 — Clustering at the unit of randomization

**Tier:** 2
**Question:** What are the Table 3 standard errors when clustered by
instructor (the unit randomized) rather than by course-section?
**Paper's statement at issue:** "Standard errors clustered at the course-
section level, the unit of randomization, are in parentheses." (Table 3
note, p. 41); "randomization occurred at the instructor level" (p. 9).
**Specification:** Re-estimate Table 3, both panels, with controls,
clustering by instructor; report the number of instructor clusters per
sample and the number of instructors who taught more than one section, by
arm.
**Output:** A 12-cell table of SEs beside the paper's; the cluster counts.
**Disclosure:** none beyond the standing rules.
**Resolution:** Reported as is; the witness states which cells change
significance level at 5% and 10%.

### B9 — Multiple comparisons in the heterogeneity tables

**Tier:** 2
**Question:** How many interaction coefficients are tested in Tables 4 and
A4, what are the multiplicity-adjusted p-values for the family of
interactions in each table, and what is the randomization-inference
p-value for the first-generation interaction on final grade?
**Paper's statement at issue:** "the estimated final-grade losses among
first-generation students were more than twice those among continuing-
generation students in both samples, raising important concerns about
potentially unequal impact of deploying AI tools." (p. 4); "Isolated
significant findings warrant caution given the number of interactions
examined" (p. 21).
**Specification:** (a) Count the interaction coefficients in each table.
(b) Romano–Wolf stepdown adjusted p-values (or Westfall–Young) for the
family of all interaction coefficients within each table, using 9,999
cluster-bootstrap replications with seed 26159803; if infeasible,
Benjamini–Hochberg q-values and say why. (c) RI p-values (B1's procedure)
for the Treated × First generation coefficient on final grade and on
homework score, both samples. (d) The counts of first-generation students
by arm in each sample, and the block-adjusted difference in the
first-generation share (Table A2 reports p = 0.000 in the exact-match
sample). (e) The first-generation interaction re-estimated with
first-generation × block fixed effects, both samples.
**Output:** Tables.
**Disclosure:** (d) as counts by arm.
**Resolution:** If the adjusted p-value for the first-generation × treated
final-grade interaction is below 0.05 in either sample and its RI p-value
is below 0.05, the abstract's statement is supported under inference that
accounts for the number of tests. If it is above 0.10 under adjustment, the
statement rests on an unadjusted test among many. Either is reported.

### B10 — Reconciliation of reported numbers

**Tier:** 3
**Question:** For each of the following, which value do the data support?
**Paper's statement at issue:** as listed.
**Specification:** (a) Uptake: "only 14.63% of treated students ever used
the VSA" (p. 14) versus 172 ÷ 1,152 = 14.93% from Table 2; report the
numerator and denominator the code uses. (b) Interaction counts: the
weekly totals in Figure 1 (p. 34) sum to several thousand more than the
"3,460 requests" classified (p. 26); report the number of interactions,
sessions, and classified requests, with the definition of each. (c)
Instructor survey response rate: 67% and 70% in consecutive sentences
(p. 14); report the number of instructor respondents and the denominator.
(d) Feedback-on-attempt share: 0.7% (pp. 4, 27) versus 7.6% (p. 28); report
the share by category from the classifier output. (e) The introduction's
"0.27–0.37 standard deviations" (p. 3): report the two estimates these
correspond to. (f) Humanities significance: the text's "1% level" (p. 22)
versus Table 5's two stars; report the p-values. (g) The discussion's
"evidence of a statistically significant difference in conditions in
full-match sample" (p. 27) against p. 19's "not significant evidence";
report the full-sample final-grade p-value with and without controls.
**Output:** A table: item, the paper's values, the value the data support.
**Disclosure:** none beyond the standing rules.
**Resolution:** Reported as is.

## Part C — Documentation

### C1 — Outcome construction

**Tier:** 1
**Question:** How is each outcome built from the ELMS and registrar exports?
**Specification:** For final grade, course letter grade, homework score, page
views, active days, total participation, homework submitted, and homework
submitted on time: the export file, the field, the export date, the
transformation in code (file and line), the handling of missing values, and
any exclusion applied. Quote code; do not quote data.
**Output:** One table, one row per outcome.

### C2 — The analysis plan and its relation to the paper

**Tier:** 2
**Question:** What does the registered analysis plan specify, and where does
the paper depart from it?
**Specification:** From the OSF document (footnote 3, p. 16; the host supplies
the file as uploaded, with its upload date): the primary outcomes, the
samples, the covariates, the significance threshold, the subgroup analyses,
the clustering, and any outcome named in the plan or the OSF project
description (including an office-hours outcome) that the paper does not
report. Tabulate each element beside what the paper does.
**Output:** A table: element, plan, paper, same/different.

### C3 — The randomization record

**Tier:** 1
**Question:** How were instructors assigned, and how did block membership
change over time?
**Specification:** The script, seed, or procedure used to assign; who or
what performed it; the dates of each assignment round; the rule applied to
instructors recruited after the semester began; the full block membership
history by block label (counts of instructors by arm at each round, not
names). Quote the assignment code if it exists.
**Output:** A description and a table by block label and round.

### C4 — Software, environment, and manual steps

**Tier:** 2
**Question:** Does the package run end to end from raw exports to the
printed tables, and where do manual steps intervene?
**Specification:** List the software and versions the code requires and
those available on the host machine; list every step that is not performed
by code (hand edits, values typed in, spreadsheet operations), with the
file it affects.
**Output:** A description and a list.

## Part D — Restrictions on the witness

- Do not open the VSA chat corpus or re-run the chat classifier; item B10(d)
  uses the classifier's existing output table only.
- Do not open free-text survey responses.
- Do not compute or write any student-level or section-level file under
  `ew/`; all outputs are aggregates under the disclosure rules above.
- Do not re-specify the paper's models beyond what an item asks. Where an
  item asks for a re-estimate, report the paper's own specification first
  and the variation second.
- The witness does not evaluate the paper's conclusions, does not propose
  alternative framings, and does not contact anyone. Questions about the
  data or the environment go to the host and are recorded as interventions.
