package main

import rego.v1

# Conftest / OPA admission: input is a rendered manifest (Conftest) or AdmissionReview (Gatekeeper-style).
containers contains c if { c := input.spec.template.spec.containers[_] }
containers contains c if { c := input.spec.containers[_] }

deny contains msg if {
	some c in containers
	c.securityContext.privileged == true
	msg := sprintf("Privileged container not allowed: %v (RBI 5.4 / PCI 2.2)", [c.name])
}

deny contains msg if {
	some c in containers
	not c.resources.limits.memory
	msg := sprintf("Memory limit required: %v", [c.name])
}

deny contains msg if {
	some c in containers
	not c.resources.limits.cpu
	msg := sprintf("CPU limit required: %v", [c.name])
}
