#!/usr/bin/env bash
# merge_verified.sh <worktree> "<merge message>" — merge a worker branch into main ONLY if the ledger has a full-suite
# PASS from review_branch.sh for the branch's exact HEAD commit. A new commit after review voids it. See STEERING.md.
#   REPO    the live checkout (default: the worktree's main repo)    LEDGER  default: tools/ledger.tsv
set -euo pipefail
WT=$(realpath "${1:?worktree}"); MSG=${2:?merge message}
REPO=$(realpath "${REPO:-$(dirname "$(git -C "$WT" rev-parse --path-format=absolute --git-common-dir)")}")
L=${LEDGER:-$(dirname "$(realpath "$0")")/ledger.tsv}
H=$(git -C "$WT" rev-parse HEAD); BR=$(git -C "$WT" rev-parse --abbrev-ref HEAD)
ROW=$( [ -f "$L" ] && awk -F'\t' -v h="$H" '$3==h' "$L" | tail -1 || true)
[ -n "$ROW" ] || { echo "refused: no review of $BR at ${H:0:8} in the ledger (run review_branch.sh)"; exit 1; }
echo "$ROW" | awk -F'\t' '$4=="PASS" && $5!="no-suite"{ok=1} END{exit !ok}' \
  || { echo "refused: last review of ${H:0:8} is not a full-suite PASS: $ROW"; exit 1; }
git -C "$WT" merge-base --is-ancestor main HEAD || { echo "refused: main moved since review; rebase and review again"; exit 1; }
[ "$(git -C "$REPO" rev-parse --abbrev-ref HEAD)" = main ] || { echo "refused: live checkout is not on main"; exit 1; }
git -C "$REPO" merge --no-ff "$BR" -m "$MSG"
echo "merged $BR (${H:0:8}) into main: $(git -C "$REPO" rev-parse --short HEAD)"
