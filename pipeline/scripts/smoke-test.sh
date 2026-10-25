#!/usr/bin/env bash
# Minimal smoke: health, login, balance, ₹1 sandbox transfer. Extend with the real suite.
set -euo pipefail
ENV=$1; BASE="https://payments.${ENV}.novapay.example"; [[ $ENV == production ]] && BASE="https://payments.novapay.example"
curl -fsS "$BASE/actuator/health/readiness" >/dev/null && echo "readiness OK"
curl -fsS -H "Authorization: Bearer ${SMOKE_TOKEN:?}" "$BASE/v1/accounts/synthetic/balance" >/dev/null && echo "balance OK"
curl -fsS -X POST -H "Authorization: Bearer $SMOKE_TOKEN" -H "Idempotency-Key: smoke-$(date +%s)" -d '{"amount":1,"currency":"INR","sandbox":true}' "$BASE/v1/transfers" >/dev/null && echo "transfer OK"
