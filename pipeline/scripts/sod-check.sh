#!/usr/bin/env bash
# Builds SoD input from GitHub API and evaluates policies/segregation-of-duties.rego. Needs GH_TOKEN, gh, jq, opa.
set -euo pipefail
PR=${PR_NUMBER:-$(gh pr list --search "$GITHUB_SHA" --state merged --json number -q '.[0].number')}
author=$(gh pr view "$PR" --json author -q .author.login)
approvers=$(gh pr view "$PR" --json reviews -q '[.reviews[] | select(.state=="APPROVED") | .author.login] | unique')
jq -n --arg a "$author" --argjson ap "$approvers" --arg d "${GITHUB_ACTOR}" \
  '{author:$a, approvers:$ap, deployer:$d, required_roles:["release-manager","sre-lead"], approver_roles:{}}' > sod-input.json
# approver_roles is populated from the IdP group export in real use
opa eval -f pretty -i sod-input.json -d "$(dirname "$0")/../policies/segregation-of-duties.rego" 'data.sod.deny'
[[ "$(opa eval -f raw -i sod-input.json -d "$(dirname "$0")/../policies/segregation-of-duties.rego" 'count(data.sod.deny)')" == "0" ]]
