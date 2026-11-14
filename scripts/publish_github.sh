#!/bin/sh
# Requires authenticated gh; publishes only the audited archive to an empty repo.
set -eu
cd "$(dirname "$0")/.."
repo=${1:-Taphinho/Projet-IAM-keycloak}
gh auth status >/dev/null
.venv/bin/python scripts/package_release.py
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
python3 -m zipfile -e dist/enterprise-iam-lab-source.zip "$stage"
git -C "$stage" init -b main
login=$(gh api user --jq .login)
uid=$(gh api user --jq .id)
git -C "$stage" config user.name "$login"
git -C "$stage" config user.email "$uid+$login@users.noreply.github.com"
git -C "$stage" add .
git -C "$stage" commit -m "Deliver Enterprise IAM lab with tested OIDC, SSO, RBAC and LDAPS"
if gh repo view "$repo" >/dev/null 2>&1; then
    if [ -n "$(git ls-remote "https://github.com/$repo.git")" ]; then
        echo "Dépôt non vide : abandon pour ne pas écraser son historique." >&2
        exit 1
    fi
    gh auth setup-git
    git -C "$stage" remote add origin "https://github.com/$repo.git"
    git -C "$stage" push -u origin main
else
    gh repo create "$repo" --public --source "$stage" --remote origin --push
fi
gh repo view "$repo" --json url --jq .url
