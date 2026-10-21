#!/bin/bash
# public_check.sh: this repository is public. Refuse anything naming the private project: product, show and mission
# names, character names, run and round ids, hosts, addresses and home paths. Run before every release (and by the
# pre-push hook). Exit 1 and print the lines when something matches.
cd "$(dirname "$0")/.." || exit 2
PAT='hitmaker|sodareel|ffas|hayaku|justblaze|campfire|spark-bfe1|\bR0[0-9]{2}\b|\br[0-9]{2,3}\b|\bRoll 1[0-9]\b|rachel|damien|caroline|cecilia|austin|leslie|amanda|holly|previz-15|script-to-hit|motion-transfer|directing-craft|roll15|\bh3:[0-9]|/mnt/|/home/[a-z]|100\.[0-9]+\.[0-9]+\.[0-9]+|127\.0\.0\.1:81[89][0-9]'
HITS=$(grep -rniE "$PAT" . --include='*.md' --include='*.sh' --include='*.py' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.txt' | grep -v '^./.git/' | grep -v '^./scripts/public_check.sh:')
if [ -n "$HITS" ]; then echo "public check FAILED: private names in a public repo:"; echo "$HITS" | cut -c1-200; exit 1; fi
echo "public check: clean"
