package sod

import rego.v1

ok_input := {
	"author": "dev1", "approvers": ["alice", "bob"], "deployer": "deploy-bot",
	"required_roles": ["release-manager", "sre-lead"],
	"approver_roles": {"alice": "release-manager", "bob": "sre-lead"},
}

test_dual_approval_allows if { allow with input as ok_input }

test_self_approval_denied if {
	i := json.patch(ok_input, [{"op": "replace", "path": "/approvers", "value": ["dev1", "bob"]}])
	not allow with input as i
	"author approved own change" in deny with input as i
}

test_single_approver_denied if {
	i := json.patch(ok_input, [{"op": "replace", "path": "/approvers", "value": ["alice"]}])
	not allow with input as i
	"fewer than 2 distinct approvers" in deny with input as i
}

test_deployer_is_author_denied if {
	i := json.patch(ok_input, [{"op": "replace", "path": "/deployer", "value": "dev1"}])
	not allow with input as i
}

test_missing_role_denied if {
	i := json.patch(ok_input, [{"op": "replace", "path": "/approver_roles", "value": {"alice": "release-manager", "bob": "developer"}}])
	not allow with input as i
}
