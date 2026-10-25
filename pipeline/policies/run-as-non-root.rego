package main

import rego.v1

deny contains msg if {
	some c in input.spec.template.spec.containers
	not c.securityContext.runAsNonRoot == true
	msg := sprintf("Container must run as non-root: %v", [c.name])
}

deny contains msg if {
	some c in input.spec.template.spec.containers
	c.securityContext.allowPrivilegeEscalation != false
	msg := sprintf("allowPrivilegeEscalation must be false: %v", [c.name])
}
