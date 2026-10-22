#!/usr/bin/env bash
# install_hooks.sh: install the expert-witness pre-commit hook in the current git repository.
#
# Usage:  bash <skill>/scripts/install_hooks.sh [--help]
#
# Run it from inside the run directory (a git checkout). It writes .git/hooks/pre-commit, which on
# every commit:
#   1. refuses the commit if any staged path is under ew-local/ (at any depth) or under the package
#      directory named in HOST.md's **Package directory:** field (HOST.md is read at commit time);
#   2. runs disclosure_check.py on the staged contents of the staged files (exported from the index,
#      so a fix made in the working tree but not staged does not count), with
#      --allow ew/disclosure/allow.txt --terms ew-local/sensitive-terms.txt, plus --pre-report with
#      the committed pre-report (HEAD:PRE-REPORT.md, so an uncommitted edit cannot widen it; the
#      working-tree file only before the first commit), so sentences quoted from the pre-report are
#      not flagged; and blocks the commit, showing the checker's output, if the check fails.
# The absolute paths of this scripts/ directory and of python3 are written into the hook now, so the
# hook finds the checker wherever the skill is installed; re-run this after moving the skill.
# A hook installed by this script is replaced; any other existing pre-commit hook is moved aside to
# pre-commit.before-expert-witness. If core.hooksPath points elsewhere, nothing is installed, since
# git would never run .git/hooks/pre-commit.
#
# Exit status: 0 when installed; 1 if this is not a git work tree, python3 or the checker is
# missing, or core.hooksPath would bypass the hook; 2 for an unknown argument.
set -euo pipefail

usage() { sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'; }
case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "") ;;
  *) echo "install_hooks.sh: unknown argument: $1" >&2; usage >&2; exit 2 ;;
esac

SCRIPTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
for f in disclosure_check.py init_report.py; do
  [ -f "$SCRIPTS_DIR/$f" ] || { echo "install_hooks.sh: $SCRIPTS_DIR/$f not found" >&2; exit 1; }
done
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "install_hooks.sh: not inside a git work tree. Run this from the run directory, the git" \
       "checkout of the shared repository." >&2
  exit 1
fi
PYTHON=$(command -v python3 || true)
[ -n "$PYTHON" ] || { echo "install_hooks.sh: python3 not found on PATH" >&2; exit 1; }

TOP=$(git rev-parse --show-toplevel)
cd "$TOP"
HOOKS="$(cd "$(git rev-parse --git-common-dir)" && pwd -P)/hooks"
mkdir -p "$HOOKS"
HOOKS_PATH=$(git config --get core.hooksPath || true)
if [ -n "$HOOKS_PATH" ]; then
  case "$HOOKS_PATH" in
    /*) RESOLVED=$HOOKS_PATH ;;
    "~"/*) RESOLVED="$HOME/${HOOKS_PATH#\~/}" ;;
    *) RESOLVED="$TOP/$HOOKS_PATH" ;;
  esac
  RESOLVED=$(cd "$RESOLVED" 2>/dev/null && pwd -P || printf '%s' "$RESOLVED")
  if [ "$RESOLVED" != "$HOOKS" ]; then
    echo "install_hooks.sh: core.hooksPath is set to '$HOOKS_PATH', so git would never run" \
         "$HOOKS/pre-commit. Nothing installed. For this repository only, run" \
         "'git config --local core.hooksPath \"$HOOKS\"' (or unset core.hooksPath) and re-run." >&2
    exit 1
  fi
fi

TARGET="$HOOKS/pre-commit"
MARK="expert-witness pre-commit hook"
if [ -e "$TARGET" ] && ! grep -q "$MARK" "$TARGET"; then
  mv "$TARGET" "$HOOKS/pre-commit.before-expert-witness"
  echo "install_hooks.sh: moved the existing pre-commit hook to $HOOKS/pre-commit.before-expert-witness" \
       "(it no longer runs)"
fi
squote() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }

{
  echo '#!/bin/sh'
  echo "# $MARK, installed by install_hooks.sh on $(date '+%Y-%m-%d %H:%M %z')."
  echo "# Re-run install_hooks.sh to update it. 'git commit --no-verify' bypasses it and the protocol."
  echo "EW_SCRIPTS=$(squote "$SCRIPTS_DIR")"
  echo "EW_PYTHON=$(squote "$PYTHON")"
  cat <<'HOOK'
NAME="pre-commit (expert-witness)"
fail() { printf '%s\n' "$@" >&2; exit 1; }

[ -x "$EW_PYTHON" ] || EW_PYTHON=$(command -v python3) || fail "$NAME: python3 not found; commit blocked."
[ -f "$EW_SCRIPTS/disclosure_check.py" ] ||
  fail "$NAME: $EW_SCRIPTS/disclosure_check.py is missing; re-run install_hooks.sh. Commit blocked."
ROOT=$(git rev-parse --show-toplevel) || exit 1
cd "$ROOT" || exit 1
WORK=$(mktemp -d "${TMPDIR:-/tmp}/ew-pre-commit.XXXXXX") || fail "$NAME: no temporary directory; commit blocked."
trap 'rm -rf "$WORK"' EXIT
git diff --cached --name-only --diff-filter=ACMRT -z | tr '\000' '\n' > "$WORK/staged" ||
  fail "$NAME: could not list the staged files; commit blocked."
[ -s "$WORK/staged" ] || exit 0

PKG=""
if [ -f HOST.md ]; then
  PKG=$("$EW_PYTHON" -I -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import init_report as r
print(r.package_dir_from_host(sys.argv[2], sys.argv[3])[0] or "")' "$EW_SCRIPTS" HOST.md "$ROOT" 2>/dev/null) || PKG=""
fi
[ -n "$PKG" ] || echo "$NAME: WARNING: no package directory could be read from HOST.md; only ew-local/ is guarded." >&2

REFUSED=""
while IFS= read -r p; do
  case "$p" in
    ew-local|ew-local/*|*/ew-local/*) REFUSED="$REFUSED
  $p  (under ew-local/)"; continue ;;
  esac
  if [ -n "$PKG" ]; then
    case "$p" in "$PKG"|"$PKG"/*) REFUSED="$REFUSED
  $p  (under the package directory $PKG/)" ;; esac
  fi
done < "$WORK/staged"
[ -z "$REFUSED" ] || fail "$NAME: commit refused. These staged paths must never be committed:$REFUSED" \
  "Unstage them (git restore --staged <path>) and make sure .gitignore lists them."

set --
while IFS= read -r p; do set -- "$@" "$p"; done < "$WORK/staged"
mkdir "$WORK/index"
git checkout-index --prefix="$WORK/index/" -- "$@" || fail "$NAME: could not export the staged files; commit blocked."
if git rev-parse --verify -q HEAD >/dev/null; then
  if git show HEAD:PRE-REPORT.md > "$WORK/PRE-REPORT.md" 2>/dev/null; then
    set -- --pre-report "$WORK/PRE-REPORT.md" -- "$@"
  else
    set -- -- "$@"
  fi
elif [ -f PRE-REPORT.md ]; then
  echo "$NAME: no commit yet, so --pre-report uses the working-tree PRE-REPORT.md." >&2
  set -- --pre-report "$ROOT/PRE-REPORT.md" -- "$@"
else
  set -- -- "$@"
fi
cd "$WORK/index" || exit 1
if "$EW_PYTHON" -I -B "$EW_SCRIPTS/disclosure_check.py" --allow "$ROOT/ew/disclosure/allow.txt" \
     --terms "$ROOT/ew-local/sensitive-terms.txt" "$@"; then
  exit 0
fi
fail "" "$NAME: commit blocked by the disclosure check above. Fix the staged files, or add a" \
  "defensible 'pattern|reason' line to ew/disclosure/allow.txt for a false positive; then stage and commit again."
HOOK
} > "$TARGET.tmp"
chmod 755 "$TARGET.tmp"
mv "$TARGET.tmp" "$TARGET"
echo "install_hooks.sh: installed $TARGET"
echo "install_hooks.sh: it runs $SCRIPTS_DIR/disclosure_check.py with $PYTHON on every commit"
