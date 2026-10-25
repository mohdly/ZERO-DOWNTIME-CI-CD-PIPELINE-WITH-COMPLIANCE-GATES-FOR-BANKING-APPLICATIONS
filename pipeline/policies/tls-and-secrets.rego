package main

import rego.v1

# No plaintext secrets in env of rendered manifests (use ExternalSecret / secretKeyRef)
deny contains msg if {
	some c in input.spec.template.spec.containers
	some e in c.env
	regex.match(`(?i)(password|secret|token|api[_-]?key)`, e.name)
	e.value
	msg := sprintf("Plaintext secret-like env var %v in %v: use secretKeyRef (PCI 3/8, RBI 5.4)", [e.name, c.name])
}

# Istio gateway servers must require TLS 1.3 minimum (when input is a Gateway)
deny contains msg if {
	input.kind == "Gateway"
	some s in input.spec.servers
	s.tls.minProtocolVersion != "TLSV1_3"
	msg := "Gateway TLS minProtocolVersion must be TLSV1_3 (RBI 5.4)"
}
