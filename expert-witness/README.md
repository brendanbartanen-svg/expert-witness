# Expert Witness

A protocol, and a Claude Code skill that follows it, for settling questions
about what a paper's data show when the code and data cannot be shared.

An editor, referee, or critic writes a **pre-report**: a fixed list of
reproduction checks and requested analyses, each specified precisely enough
that two people would compute the same number, with the resolution stated
in both directions before anyone has seen the answer. The authors (or a
third party holding the materials on their behalf) run the skill in their
own environment, on their own Claude account, at the model and effort the
pre-report asks for. The skill answers the items, applies the disclosure
rules the host declared (FERPA, IRB, data-use terms), and pushes a full
report, with every script and log, to a private repository that the
authors, the editor, the referees, and the requester can all read. Everyone
sees it at the same moment.

The witness is a judge, not a prosecutor. It computes what was asked,
reports results in both directions with the same care, characterizes no
one's motives, and rates nothing.

## What each party does

**The requester** writes `PRE-REPORT.md` from `assets/PRE-REPORT-TEMPLATE.md`
and commits it to the repository first. The questions must be on the record
before the run; the witness refuses to start if the pre-report in the
checkout differs from the one at the remote.

**The host** prepares a run directory:

```
ew-run/                      a fresh git checkout of the shared repository
  PRE-REPORT.md              committed by the requester
  HOST.md                    committed by the host, from assets/HOST-TEMPLATE.md
  package/                   a COPY of the code and data; the originals live elsewhere
  ew-local/                  created by the host; gitignored
    sensitive-terms.txt      instructor names, course titles, internal names (never committed)
```

Then, with the skill installed (copy this folder to `~/.claude/skills/expert-witness/`
or open the `.skill` file), start Claude Code in `ew-run/` on the model the
pre-report names and say:

> Run the expert witness on PRE-REPORT.md.

Nothing more. Anything else said to the witness during the run is recorded
in the report as an intervention, including requests to change, soften, or
delay. A clarification of fact ("the export is in `data/raw/`, not `old/`")
is accepted and recorded; a change to a question is declined and recorded.

**Everyone with read access** can watch the repository as the run commits
after each phase and each item, and reads `REPORT.md` when the tag
`report-v1` appears.

## What the witness will not do

Report anything about an individual student or an identifiable instructor;
quote any chat, message, or free-text answer; write to the originals; reach
the network except the git remote and declared package installs; run a
script it has not read; edit the pre-report or the report after its tag;
show the host a draft; evaluate the paper's conclusions.

## What it cannot do

It cannot make a hostile host honest. A host can delete the run before it
pushes. What the protocol guarantees is that an honest host's run is
legible and reproducible by a third party given the same package, and that
any departure from the protocol during the run is visible: progress is
pushed as it happens, interventions are logged verbatim, and the absence of
a final tag is itself a finding. A third-party host removes the remaining
gap; the protocol is the same either way.

## Contents

```
SKILL.md                     the instructions the witness follows
references/protocol.md       phases and decision rules
references/disclosure.md     what may leave the machine, and how it is checked
references/report-template.md
references/running-code.md   Stata/R/Python in batch; side-effect review
assets/PRE-REPORT-TEMPLATE.md
assets/HOST-TEMPLATE.md
scripts/init_report.py       REPORT.md skeleton from the pre-report; ew/ tree; .gitignore
scripts/census.py            package inventory with hashes; executes nothing
scripts/compare.py           reported vs reproduced cells, with tolerance
scripts/disclosure_check.py  identifier and small-cell scan; used by the pre-commit hook
scripts/install_hooks.sh     installs the hook
```
