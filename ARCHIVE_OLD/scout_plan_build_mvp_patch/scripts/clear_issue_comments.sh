#!/bin/bash
# Clear all comments from a GitHub issue
# Usage: ./scripts/clear_issue_comments.sh <issue-number>
set -e
if [ $# -eq 0 ]; then
    echo "Usage: $0 <issue-number>"; exit 1; fi
ISSUE_NUMBER=$1
if [ -f .env ]; then export $(cat .env | grep -v '^#' | xargs); fi
GITHUB_REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$GITHUB_REPO_URL" ]; then echo "Error: Not in a git repo"; exit 1; fi
REPO_PATH=$(echo $GITHUB_REPO_URL | sed 's|https://github.com/||' | sed 's|.git$||')
if [ -n "$GITHUB_PAT" ]; then export GH_TOKEN=$GITHUB_PAT; fi
COMMENT_IDS=$(gh api repos/$REPO_PATH/issues/$ISSUE_NUMBER/comments --jq '.[].id' 2>/dev/null || echo "")
if [ -z "$COMMENT_IDS" ]; then echo "No comments found"; exit 0; fi
for COMMENT_ID in $COMMENT_IDS; do
    gh api --method DELETE repos/$REPO_PATH/issues/comments/$COMMENT_ID 2>/dev/null || echo "Failed $COMMENT_ID"
done
echo "✅ Deleted all comments from issue #$ISSUE_NUMBER"
