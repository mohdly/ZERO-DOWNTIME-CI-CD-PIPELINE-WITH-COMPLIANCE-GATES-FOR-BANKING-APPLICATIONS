-- EXPAND: backward compatible. App V(N-1) ignores the new column.
-- Flyway: this script contains CREATE INDEX CONCURRENTLY, so it MUST run outside a transaction
-- (see V2.0__expand_add_encrypted_email.sql.conf -> executeInTransaction=false).
SET lock_timeout = '3s';
SET statement_timeout = '60s';

ALTER TABLE customer_profiles ADD COLUMN IF NOT EXISTS encrypted_email BYTEA;

SET statement_timeout = 0;  -- index build on 100M rows takes long; concurrent build doesn't block writes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_encrypted_email
  ON customer_profiles (encrypted_email);

INSERT INTO schema_audit_log (migration_id, description, executed_by, phase)
VALUES ('V2.0', 'Add encrypted_email column', current_user, 'EXPAND');
-- Do NOT drop email here. CONTRACT happens in V2.2 after all services migrate.
