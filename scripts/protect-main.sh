#!/usr/bin/env sh
# Branch protection for main (tech.md, 16.2): PR only, required checks, squash merge, no approvals.
# Usage: scripts/protect-main.sh <owner>/<repo> [extra required check, e.g. e2e]
set -eu
repo="$1"
extra="${2:-}"
checks='"front","back","drift","contract-guard"'
[ -n "$extra" ] && checks="$checks,\"$extra\""

gh repo edit "$repo" --enable-squash-merge --enable-merge-commit=false \
  --enable-rebase-merge=false --delete-branch-on-merge

gh api -X PUT "repos/$repo/branches/main/protection" --input - <<JSON
{
  "required_status_checks": {"strict": true, "contexts": [$checks]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
