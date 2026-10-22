#!/bin/bash
# public_check.sh: this repository is public. Refuse anything that names the private project (its products, shows,
# missions, characters, run and round ids, hosts, addresses, home paths). Run before every release and by the pre-push
# hook. The patterns live in a private file on the maintainer's machine, never in this repository; without that file
# the check fails, so nothing is pushed unchecked. Exit 1 and print the lines when something matches.
cd "$(dirname "$0")/.." || exit 2
LIST=${PUBLIC_DENYLIST:-$HOME/AI/handoffs/private/public_denylist.txt}
if [ ! -r "$LIST" ]; then
  echo "public check FAILED: the private denylist is missing ($LIST). Set PUBLIC_DENYLIST to its path; nothing is checked without it."
  exit 2
fi
PAT=$(grep -v '^\s*#' "$LIST" | grep -v '^\s*$' | paste -sd'|')
[ -n "$PAT" ] || { echo "public check FAILED: the denylist $LIST is empty"; exit 2; }
HITS=$(grep -rniE "$PAT" . --include='*.md' --include='*.sh' --include='*.py' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.txt' | grep -v '^./.git/')
if [ -n "$HITS" ]; then echo "public check FAILED: private names in a public repo:"; echo "$HITS" | cut -c1-200; exit 1; fi
echo "public check: clean"
