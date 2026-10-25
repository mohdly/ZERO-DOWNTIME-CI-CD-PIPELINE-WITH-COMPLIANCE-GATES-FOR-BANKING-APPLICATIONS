#!/usr/bin/env python3
"""MIGRATE phase backfill: idempotent, resumable, throttled, abortable. Requires psycopg[binary], boto3 (KMS)."""
import os, sys, time, psycopg

BATCH = int(os.getenv("BATCH_SIZE", 10_000))
MAX_LAG_S = float(os.getenv("MAX_REPLICA_LAG_S", 5))
BASELINE_P95_MS = float(os.getenv("BASELINE_P95_MS", 40))
MAX_IMPACT = 1.20  # abort/pause if p95 > baseline * 1.2

def encrypt(plaintext: str) -> bytes:  # replace with envelope encryption via KMS data key
    raise NotImplementedError("wire to KMS/Vault transit; never log plaintext")

def replica_lag(cur) -> float:
    cur.execute("SELECT COALESCE(EXTRACT(EPOCH FROM max(replay_lag)),0) FROM pg_stat_replication")
    return float(cur.fetchone()[0])

def p95_ms() -> float:  # query Prometheus in real life
    return float(os.getenv("CURRENT_P95_MS", BASELINE_P95_MS))

def main():
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT COALESCE(max(last_id),0) FROM backfill_checkpoint WHERE job='encrypt_email'")
        last = cur.fetchone()[0]
        total = 0
        while True:
            if replica_lag(cur) > MAX_LAG_S or p95_ms() > BASELINE_P95_MS * MAX_IMPACT:
                time.sleep(5); continue                     # pause (hard abort after N pauses in prod)
            t0 = time.time()
            cur.execute("""SELECT id, email FROM customer_profiles
                           WHERE id > %s AND encrypted_email IS NULL AND email IS NOT NULL
                           ORDER BY id LIMIT %s""", (last, BATCH))
            rows = cur.fetchall()
            if not rows: break
            with conn.transaction():                        # one short transaction per batch
                cur.executemany("UPDATE customer_profiles SET encrypted_email=%s WHERE id=%s AND encrypted_email IS NULL",
                                [(encrypt(e), i) for i, e in rows])
                last = rows[-1][0]
                cur.execute("INSERT INTO backfill_checkpoint(job,last_id) VALUES('encrypt_email',%s)", (last,))
            total += len(rows)
            print(f"migrated={total} last_id={last}", flush=True)
            time.sleep(max(0.1, 2 * (time.time() - t0)))    # adaptive throttle
        cur.execute("SELECT count(*) FROM customer_profiles WHERE encrypted_email IS NULL AND email IS NOT NULL")
        if cur.fetchone()[0]:
            sys.exit("Migration incomplete: rows with email but no encrypted_email")

if __name__ == "__main__":
    main()
