package sod

import rego.v1

# input: { "author": "...", "approvers": ["..."], "deployer": "...", "required_roles": ["release-manager","sre-lead"], "approver_roles": {"alice":"release-manager","bob":"sre-lead"} }
default allow := false

allow if {
	count(deny) == 0
}

deny contains "author approved own change" if { input.author in input.approvers }
deny contains "deployer is author" if { input.deployer == input.author }
deny contains "deployer is an approver" if { input.deployer in input.approvers }
deny contains "fewer than 2 distinct approvers" if { count({a | some a in input.approvers}) < 2 }
deny contains msg if {
	some r in input.required_roles
	not role_covered(r)
	msg := sprintf("missing approval from role %v", [r])
}
role_covered(r) if { some a in input.approvers; input.approver_roles[a] == r }
