package main

import rego.v1

good_pod := {"spec": {"template": {"spec": {"containers": [{
	"name": "payments-api",
	"image": "registry.novapay.internal/novapay/payments-api@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
	"securityContext": {"runAsNonRoot": true, "allowPrivilegeEscalation": false, "privileged": false},
	"resources": {"limits": {"cpu": "1", "memory": "1Gi"}},
	"env": [{"name": "DB_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "db", "key": "pw"}}}],
}]}}}}

test_good_manifest_has_no_denies if {
	count(deny) == 0 with input as good_pod
}

test_latest_tag_denied if {
	bad := json.patch(good_pod, [{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "registry.novapay.internal/novapay/payments-api:latest"}])
	some msg in deny with input as bad
	contains(msg, "pinned by digest")
}

test_privileged_denied if {
	bad := json.patch(good_pod, [{"op": "replace", "path": "/spec/template/spec/containers/0/securityContext/privileged", "value": true}])
	some msg in deny with input as bad
	contains(msg, "Privileged")
}

test_missing_memory_limit_denied if {
	bad := json.patch(good_pod, [{"op": "remove", "path": "/spec/template/spec/containers/0/resources/limits/memory"}])
	some msg in deny with input as bad
	contains(msg, "Memory limit")
}

test_root_user_denied if {
	bad := json.patch(good_pod, [{"op": "replace", "path": "/spec/template/spec/containers/0/securityContext/runAsNonRoot", "value": false}])
	some msg in deny with input as bad
	contains(msg, "non-root")
}

test_plaintext_secret_env_denied if {
	bad := json.patch(good_pod, [{"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [{"name": "DB_PASSWORD", "value": "hunter2"}]}])
	some msg in deny with input as bad
	contains(msg, "Plaintext secret")
}

test_gateway_requires_tls13 if {
	gw := {"kind": "Gateway", "spec": {"servers": [{"tls": {"minProtocolVersion": "TLSV1_2"}}]}}
	some msg in deny with input as gw
	contains(msg, "TLSV1_3")
}

test_gateway_tls13_ok if {
	gw := {"kind": "Gateway", "spec": {"servers": [{"tls": {"minProtocolVersion": "TLSV1_3"}}]}}
	count(deny) == 0 with input as gw
}
