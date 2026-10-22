# Pre-report: {paper title}

A pre-report is the report with the answers blank. It fixes the questions
before anyone has seen the data, so that the answers cannot shape them. The
witness copies each item's title and question into `REPORT.md` verbatim and
fills in the rest. Items are parsed by their headings, so keep the form:
`### {ID} — {title}` with IDs `A1…`, `B1…`, `C1…`, and the bold field labels
below exactly as written.

## Header

- **Paper:** {authors, title, venue or series, version date}
- **Artifact under examination:** {file name}; SHA-256 {hash}. Page numbers
  below are {printed | PDF} pages.
- **Requester:** {name, role: editor | referee | reader}; {affiliation}
- **Requester's declarations:** {interest in the paper; prior public
  statements about it; commitments about how the report will be used}
- **Host:** {the authors | a third-party environment}; see `HOST.md`
- **Repository:** {URL}; read access: {authors, editor, referees, requester}
- **Model and effort requested:** {model id}; effort {level}; acceptable
  substitutes: {…}. The report records what was actually used.
- **Tiers:** Tier 1 items are released as `report-v1` before the rest if the
  host's budget requires; tiers 2 and 3 follow as `report-v2`.
- **Date fixed:** {date the pre-report was committed}

## Scope

{Two or three sentences on what is in dispute, written so that both parties
would accept the description. Then the standing rule:}

The witness answers the items below, reports in both directions with equal
care, characterizes no one's motives, rates nothing, and reports anything
encountered that bears on an item under that item's Observations. Matters
outside the items are listed in one line each without analysis.

## Disclosure rules for this run

- Minimum cell count: {10}. Suppressed cells print `<{n}`.
- Section-level rows under random labels: {permitted | not permitted}.
- Course identification: block labels as printed in the paper only.
- Text from chats, free-text survey answers, or messages: none.
- {Any further rule from the requester.} `HOST.md` may tighten any of these.

## Part A — Reproduction

Run the authors' code as shipped and compare its output with the printed
exhibits. One item per exhibit or group of exhibits.

### A1 — {exhibit}

**Tier:** {1 | 2 | 3}
**Exhibits:** {Table 3, Panels A and B, with and without controls}
**Cells:** {all | the following: …}
**Notes:** {anything the witness should know: units, which sample, where
the control SDs come from}

## Part B — Requested analyses

Each item: a question in plain language; a specification precise enough
that two witnesses would compute the same number; the output shape; the
disclosure constraints specific to the item; and a resolution statement
written in both directions.

### B1 — {title}

**Tier:** {1 | 2 | 3}
**Question:** {one or two sentences, in plain language}
**Paper's statement at issue:** "{quoted sentence}" (p. {n})
**Specification:** {what to compute, from which file, with which sample,
controls, fixed effects, clustering, seeds; what to hold fixed from the
paper and what to vary}
**Output:** {the table shape; units; both raw and SD units if the paper
uses both}
**Disclosure:** {item-specific constraints; what to coarsen if needed}
**Resolution:** If {outcome X}, the paper's statement is {supported |
not supported} in the sense that {…}. If {outcome Y}, {…}. Either is
reported without characterization.

## Part C — Documentation

Questions whose answer is a description of code, data, or procedure
rather than a number.

### C1 — {title}

**Tier:** {1 | 2 | 3}
**Question:** {…}
**Specification:** {what to look for and where; what to quote (code and
documentation may be quoted; data may not)}
**Output:** {a description; a table of deviations; a file-and-line list}

## Part D — Restrictions on the witness

- {Things the witness must not do in this run beyond the skill's standing
  rules: for example, "do not re-run the chat classifier", "do not open the
  chat corpus", "do not compute anything at the student level that is
  written to disk".}
- The witness does not evaluate the paper's conclusions, propose
  alternative framings, or contact anyone.
