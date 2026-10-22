# Host declaration

Filled in by whoever runs the witness: the authors, or the operator of a
third-party environment. Committed to the repository before the run so
that everyone can see the terms the witness worked under. Nothing in this
file may loosen the pre-report's disclosure rules; it may tighten them.

## Who and where

- **Host:** {authors | third party}; contact for factual questions during
  the run: {role, not name, if the file is shared outside the team}
- **Run directory:** {absolute path of the git checkout the witness works in}
- **Package directory:** {path, relative to the run directory, of the COPY
  of the code and data}
  (`init_report.py` adds this path to `.gitignore`; the data never enter
  the repository)
- **Originals:** {absolute path of the originals, which the witness never
  writes to | "not on this machine"}
- **Branch:** {main}

## Environment

- **OS:** {…}
- **Software available:** {Stata 18 MP at /path; R 4.4.1; Python 3.12; …}
- **Package installs permitted:** {none | Stata ssc packages | R CRAN
  packages | Python packages from requirements.txt} — every install is
  recorded in the report with its version.
- **Network:** git remote only, plus the installs above.
- **Budget:** {wall-clock hours the host can give the run}; the witness
  releases `report-v1` at the end of tier 1 if this would be exceeded.
- **Model and effort in use:** {model id; effort setting}

## Disclosure terms that bind this run

- **Governing instruments:** {IRB protocol number; data-use agreement; FERPA}
- **Minimum cell count:** {≥ the pre-report's value}
- **Section-level rows under random labels:** {permitted | not permitted}
- **Additional restrictions:** {for example: no instructor rank by block;
  no results by class year; survey free text must not be opened}
- **Sensitive-terms file:** `ew-local/sensitive-terms.txt` (instructor
  names, course titles, internal system names; one per line; gitignored;
  listed in the report by hash only)

## What is in the package

- {Raw exports and their dates; intermediate files; the analysis file;
  code; the README; anything the pre-report asks for that is NOT in the
  package and will be supplied during the run as a clarification of fact}

## Acknowledgements

By committing this file the host agrees that the witness pushes the report
directly to the repository on completion without the host's prior review;
that instructions given to the witness during the run are recorded
verbatim in the report; and that stopping the run is recorded as such.
