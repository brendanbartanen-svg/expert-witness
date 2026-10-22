# Intake: @TITLE@

Filled in by the witness before anything else happens (protocol.md, section 1). Every {…} is a
placeholder; a field that does not apply says `none`.

## Run

- **Started:** {date and time, with time zone}
- **Ended:** {date and time}
- **Wall-clock by phase:** census {m}m; read {m}m; reproduce {m}m; items {m}m; review {m}m

## Model and effort

- **Model in use:** {model id, as the witness knows it}
- **Effort in use:** {effort setting, if the host stated it | not stated}
- **Requested by the pre-report:** {model}; effort {effort}; acceptable substitutes {…}

## Repository

- **HEAD at intake:** {git rev-parse HEAD}
- **Branch:** {branch}
- **Remote:** {remote URL, with any token removed}
- **PRE-REPORT.md blob:** {git rev-parse HEAD:PRE-REPORT.md}; same as the remote's: {yes | no}
- **HOST.md blob:** {git rev-parse HEAD:HOST.md}

## Package and environment (from HOST.md)

- **Package directory:** {path relative to the run directory}
- **Originals:** {absolute path, never written to | not on this machine}
- **Software HOST.md says is available:** {…}
- **Package installs permitted:** {…}
- **Budget:** {…}

## Disclosure terms in force

| Point | Pre-report | HOST.md | In force (the stricter) |
|---|---|---|---|
| Minimum cell count | {…} | {…} | {…} |
| Section-level rows under random labels | {…} | {…} | {…} |
| Course identification | {…} | {…} | {…} |
| Text from chats, free-text answers, messages | {…} | {…} | {…} |
| Further rules | {…} | {…} | {…} |

- **Sensitive-terms file:** ew-local/sensitive-terms.txt; under ew-local/ and gitignored: {yes | moved there from …}; SHA-256 {hash}

## Census notes

{contents the pre-report says the package should not hold (rosters, chat logs with text), and how they are handled | none}

## Supplied during the run

| File | SHA-256 | Intervention (timestamp) | Replaces (file and SHA-256) |
|---|---|---|---|
| {…} | {…} | {…} | {… \| none} |
