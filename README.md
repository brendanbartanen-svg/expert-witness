# Expert Witness

A protocol, and a Claude Code skill that follows it, for settling questions
about what a paper's data show when the code and data cannot be shared.

The problem it addresses is a familiar impasse. A reader or referee raises
specific questions about a paper's results. The authors reply. Neither side
can move the other, because the only thing that would settle it, running the
checks on the actual data, is something only the authors can do, and a
result they report themselves carries no more weight than the paper did.

The protocol:

1. The **requester** (an editor, a referee, or a reader) writes a
   **pre-report**: a fixed list of reproduction checks and requested
   analyses, each specified precisely enough that two people would compute
   the same number, with what would count as resolving it stated in both
   directions. It is committed to a private repository before any answer
   exists, so the questions are on the record first.
2. The **host** (the authors, or a third party holding the materials on
   their behalf) commits a declaration of the environment and the disclosure
   terms that bind the run (FERPA, IRB, data-use agreement), then runs the
   skill in their own environment, on their own Claude account, at the model
   and effort the pre-report names.
3. The **witness** answers the items, applies the disclosure rules
   (aggregates only, minimum cell counts, no identifiers, no text from
   subjects), and pushes a full report, with every script and log, to the
   repository. It commits after every phase and every item, records verbatim
   anything the host says to it during the run, and tags the report once.
   Authors, editor, referees, and requester read it at the same moment.

The witness is a judge, not a prosecutor. It computes what was asked,
reports results in both directions with the same care, characterizes no
one's motives, and rates nothing. It cannot make a hostile host honest; it
makes an honest host's run legible and reproducible, and any departure from
the protocol visible. A third-party host closes the remaining gap.

## Contents

- [`expert-witness/`](expert-witness/) — the skill: `SKILL.md`, the protocol
  and disclosure references, the report template, the pre-report and host
  templates, and the scripts (stdlib Python; 45 tests). Its
  [README](expert-witness/README.md) explains what each party does.
- [`pre-reports/`](pre-reports/) — pre-reports that have been offered,
  one folder per paper.
- Releases carry `expert-witness.skill`, the packaged skill, for hosts who
  install skills from a file.

## Installing the skill

Copy `expert-witness/` to `~/.claude/skills/expert-witness/`, or open the
`.skill` file from the latest release in Claude Code. Then, in a run
directory prepared as the skill's README describes:

> Run the expert witness on PRE-REPORT.md.

## Status

Version 0.1. The scripts are tested and the commit-and-hook flow has been
rehearsed, but the skill has not yet been run end to end against a real
code-and-data package. Treat the first real run as part of the development.

## Where this sits

The pieces have precedents: adversarial collaboration (a neutral arbiter
runs the design both sides agreed to), journal data editors who rerun code
before publication, the AEA's third-party verification protocol for
restricted data, cascad's certification inside France's secure data centre,
statistical-agency output checking and the SACRO/ACRO tools that automate
it, and the Institute for Replication's reproduction games. What is new here
is the combination: the questions come from the critic and are fixed with
their resolutions in advance; the run costs tens of dollars rather than
staff-days; and the report reaches everyone at once rather than passing
through the authors.

## License

MIT. See [LICENSE](LICENSE).
