#!/usr/bin/env bash
# wt_new.sh <name> — create a worktree for one worker, OUTSIDE the live checkout, on a new branch from main.
# The orchestrator runs this before briefing and gives the worker the absolute path (STEERING.md, failure #1).
#   REPO       the live checkout            (default: current git repo)
#   WT_PREFIX  where worktrees go           (default: <parent of REPO>/wt-)
set -euo pipefail
N=${1:?branch name}
REPO=${REPO:-$(git rev-parse --show-toplevel)}; REPO=$(realpath "$REPO")
WT="${WT_PREFIX:-$(dirname "$REPO")/wt-}$N"
case "$(realpath -m "$WT")" in "$REPO"/*) echo "refused: $WT is inside the live checkout"; exit 1;; esac
[ -e "$WT" ] && { echo "exists: $WT"; exit 1; }
git -C "$REPO" worktree add -q "$WT" -b "$N" main
echo "$(realpath "$WT")  (branch $N from $(git -C "$REPO" rev-parse --short main))"
