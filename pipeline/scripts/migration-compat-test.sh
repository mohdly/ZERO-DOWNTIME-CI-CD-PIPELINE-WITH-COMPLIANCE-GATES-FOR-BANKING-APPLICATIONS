#!/usr/bin/env bash
# Apply next migration to snapshot, then run contract tests for every app version marked compatible (see docs/04 matrix).
set -euo pipefail
echo "flyway migrate (executeInTransaction per script config)"; ./gradlew flywayMigrate -Pflyway.url="$DB_URL"
for v in N-1 N; do echo "contract tests for app $v"; ./gradlew pactVerify -PappVersion=$v; done
