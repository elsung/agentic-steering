#!/usr/bin/env bash
# review_branch.sh <worktree> [--no-suite] — mechanical checks to run BEFORE reading a worker's claims.
# Prints FAIL and WARN lines, then PASS or FAIL. See STEERING.md.
#   REPO       the live checkout (default: the worktree's main repo)
#   TEST_CMD   full test suite command, run in the worktree (default: python -m pytest -q)
#   API_FILE   a file whose quoted JSON keys should not disappear (optional, e.g. src/app/api.py)
set -uo pipefail
WT=$(realpath "${1:?worktree}"); fail=0
F(){ echo "FAIL: $*"; fail=1; }; W(){ echo "WARN: $*"; }
cd "$WT" || exit 2
REPO=$(realpath "${REPO:-$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")}")
echo "branch $(git rev-parse --abbrev-ref HEAD) at $(git rev-parse --short HEAD), $WT"
case "$WT" in "$REPO"/*) F "worktree is inside the live checkout";; esac
git merge-base --is-ancestor main HEAD || F "branch does not contain current main (rebase first)"
git diff --quiet && git diff --cached --quiet || F "uncommitted changes: $(git status --short | grep -v '^??' | wc -l) files"
git diff --name-only main...HEAD | grep -E '(^|/)RESULT\.md$|_scratch/|\.pyc$' && F "junk committed (above)"
git diff --diff-filter=D --name-only main...HEAD -- tests | sed 's/^/deleted test file: /' | grep . && F "test files deleted"
DT=$(git diff main...HEAD -- tests | grep -E '^-\s*(async )?def test_' | sed 's/^-\s*//' | sort)
AT=$(git diff main...HEAD -- tests | grep -E '^\+\s*(async )?def test_' | sed 's/^+\s*//' | sort)
GONE=$(comm -23 <(echo "$DT") <(echo "$AT") | grep . || true)
[ -n "$GONE" ] && F "test functions removed: $(echo $GONE | tr '\n' ' ')"
CA=$(git diff main...HEAD -- tests | grep -cE '^-\s*assert' || true)
[ "$CA" -gt 0 ] && W "$CA assert lines removed or changed in tests (check they were not weakened)"
git diff main...HEAD | grep -E '^\+.*"[a-z]{2,5}" \+ "[a-z]{2,6}"' && F "string split in added code (dodging a check?)"
git diff --numstat main...HEAD | awk '$2>40 && $2>2*$1 {print "WARN: "$3" deletes "$2" lines, adds "$1}'
if [ -n "${API_FILE:-}" ] && [ -f "$API_FILE" ]; then
  K(){ grep -oE '"[a-z_]+":' | sort -u; }
  RK=$(comm -23 <(git show "$(git merge-base main HEAD):$API_FILE" | K) <(K < "$API_FILE") | tr '\n' ' ')
  [ -n "${RK// }" ] && W "keys no longer in $API_FILE (check API responses): $RK"
fi
if [ "${2:-}" != "--no-suite" ]; then
  S=$(eval "${TEST_CMD:-python -m pytest -q -p no:cacheprovider}" 2>&1 | grep -E '^FAILED|^ERROR|passed|failed' | tail -8)
  echo "$S"
  echo "$S" | grep -qE 'failed|^FAILED|^ERROR' && F "test suite"
  echo "$S" | grep -q passed || F "no suite summary"
fi
[ $fail = 0 ] && echo "PASS" || echo "FAIL"; exit $fail
