#!/usr/bin/env bash
# Request a protected squash merge and report its actual state.
set -euo pipefail

number="${1:?Pull request number is required}"
head_sha="${2:?Validated head SHA is required}"
: "${GITHUB_REPOSITORY:?Repository is required}"
: "${GITHUB_STEP_SUMMARY:?Step summary path is required}"

actual_head="$(gh pr view "$number" --repo "$GITHUB_REPOSITORY" --json headRefOid --jq '.headRefOid')"
[[ "$actual_head" == "$head_sha" ]] || {
  echo "::error::PR head changed after verification. Aborting auto-merge request."
  exit 1
}

# GitHub keeps the request pending until required approvals and checks pass.
# Never use administrator bypass or approve the bot's own pull request.
if ! gh pr merge "$number" --repo "$GITHUB_REPOSITORY" \
  --auto --squash --delete-branch --match-head-commit "$head_sha"; then
  echo "::error::Could not enable auto-merge for PR #$number. Check repository auto-merge settings and token permissions."
  exit 1
fi

outcome="$(gh pr view "$number" --repo "$GITHUB_REPOSITORY" \
  --json mergedAt,autoMergeRequest \
  --jq 'if .mergedAt != null then "merged" elif .autoMergeRequest != null then "pending" else "missing" end')"
url="https://github.com/$GITHUB_REPOSITORY/pull/$number"
case "$outcome" in
  merged)
    echo "Gallery PR #$number validated and squash-merged: $url" >> "$GITHUB_STEP_SUMMARY"
    ;;
  pending)
    echo "Gallery PR #$number validated; auto-merge enabled, awaiting required approvals/checks: $url" >> "$GITHUB_STEP_SUMMARY"
    ;;
  *)
    echo "::error::PR #$number is neither merged nor queued for auto-merge."
    exit 1
    ;;
esac
