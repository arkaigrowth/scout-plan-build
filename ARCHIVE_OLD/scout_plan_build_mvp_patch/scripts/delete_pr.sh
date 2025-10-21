#!/bin/bash
set -e
if [ $# -eq 0 ]; then echo "Usage: $0 <pr-number> [--delete-branch]"; exit 1; fi
PR_NUMBER=$1; DELETE_BRANCH=false; [ "$2" = "--delete-branch" ] && DELETE_BRANCH=true
if [ -f .env ]; then export $(cat .env | grep -v '^#' | xargs); fi
GITHUB_REPO_URL=$(git remote get-url origin 2>/dev/null || echo ""); [ -z "$GITHUB_REPO_URL" ] && { echo "No origin remote"; exit 1; }
REPO_PATH=$(echo $GITHUB_REPO_URL | sed 's|https://github.com/||' | sed 's|.git$||')
[ -n "$GITHUB_PAT" ] && export GH_TOKEN=$GITHUB_PAT
PR_INFO=$(gh pr view $PR_NUMBER -R $REPO_PATH --json number,title,state,headRefName 2>/dev/null || echo "")
[ -z "$PR_INFO" ] && { echo "PR not found"; exit 1; }
PR_STATE=$(echo $PR_INFO | jq -r '.state'); PR_BRANCH=$(echo $PR_INFO | jq -r '.headRefName')
[ "$PR_STATE" = "OPEN" ] && gh pr close $PR_NUMBER -R $REPO_PATH || echo "PR already closed"
if $DELETE_BRANCH; then
    git push origin --delete $PR_BRANCH 2>/dev/null || true
    if git show-ref --verify --quiet refs/heads/$PR_BRANCH; then
        [ "$(git branch --show-current)" = "$PR_BRANCH" ] && git checkout main
        git branch -D $PR_BRANCH 2>/dev/null || true
    fi
    echo "✅ Closed PR and deleted branch '$PR_BRANCH'"
else
    echo "✅ Closed PR (kept branch '$PR_BRANCH')"
fi
