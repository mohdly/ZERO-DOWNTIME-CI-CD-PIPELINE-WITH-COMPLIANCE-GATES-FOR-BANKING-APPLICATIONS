package main

import rego.v1

deny contains msg if {
	some c in input.spec.template.spec.containers
	not contains(c.image, "@sha256:")
	msg := sprintf("Image must be pinned by digest (no tags/latest): %v", [c.image])
}
