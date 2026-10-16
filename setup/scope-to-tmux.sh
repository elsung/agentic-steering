#!/usr/bin/env bash
# Make every NEW window/pane (and every subagent) in one tmux session run on the small model,
# without changing the default for Claude sessions outside that tmux session.
#
# Usage: setup/scope-to-tmux.sh <tmux-session> [model-id] [effort]
# Already-running windows: type `/model <model-id>` and `/effort <effort>` in each idle one,
# then run this script again. It restores the machine-wide defaults that /model and /effort overwrite.
set -euo pipefail

SESSION=${1:?tmux session name}
MODEL=${2:-claude-haiku-5-5}
EFFORT=${3:-high}
SETTINGS="$HOME/.claude/settings.json"

tmux set-environment -t "$SESSION" CLAUDE_CODE_SUBAGENT_MODEL "$MODEL"
tmux set-environment -t "$SESSION" CLAUDE_CODE_SUBAGENT_MODEL_FORCE 1
tmux set-environment -t "$SESSION" ANTHROPIC_MODEL "$MODEL"
tmux set-environment -t "$SESSION" CLAUDE_CODE_EFFORT_LEVEL "$EFFORT"
tmux show-environment -t "$SESSION" | grep -E 'SUBAGENT|ANTHROPIC_MODEL|EFFORT'

# /model and /effort save a machine-wide default. Put back what was there before the first run.
if [ -f "$SETTINGS" ]; then
  BACKUP="$SETTINGS.before-tmux-scope"
  [ -f "$BACKUP" ] || cp "$SETTINGS" "$BACKUP"
  python3 - "$SETTINGS" "$BACKUP" <<'EOF'
import json, sys
cur, before = (json.load(open(p)) for p in sys.argv[1:3])
for key in ("model", "effortLevel"):
    if key in before: cur[key] = before[key]
    else: cur.pop(key, None)
json.dump(cur, open(sys.argv[1], "w"), indent=2)
print("machine-wide defaults:", {k: cur.get(k) for k in ("model", "effortLevel")})
EOF
fi
echo "Start the orchestrator window explicitly: claude --model opus"
