-- CONTRACT (forward-only). Separate release; CAB + DBA approval; run only after:
--  1) Pact broker shows zero deployed consumers < N+1
--  2) pg_stat_statements shows zero reads of "email" for >= 1 full release cycle
--  3) reconciliation query returns 0 rows (see docs/04 §5)
--  4) logical snapshot of the column exists in the audit bucket
SET lock_timeout = '3s';
ALTER TABLE customer_profiles DROP COLUMN email;  -- metadata-only in PostgreSQL; fast
INSERT INTO schema_audit_log (migration_id, description, executed_by, phase)
VALUES ('V2.2', 'Drop legacy email column', current_user, 'CONTRACT');
