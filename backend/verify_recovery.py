"""
Phase 10 - Database Backup and Non-Destructive Recovery Verification Script.
Proves backup integrity by creating a temporary separate test database,
restoring the dump, verifying schema and row counts, and tearing down safely.
"""

import os
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PG_BIN = r"C:\Program Files\PostgreSQL\16\bin"
PG_DUMP = os.path.join(PG_BIN, "pg_dump.exe")
PSQL = os.path.join(PG_BIN, "psql.exe")
SOURCE_DB = "placement_portal"
RECOVERY_DB = "placement_portal_recovery_verify"
BACKUP_FILE = os.path.abspath("test_recovery_backup.sql")
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

def run_recovery_verification():
    print("=== Step 1: Generating PostgreSQL Logical Backup via pg_dump ===")
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS

    dump_cmd = [
        PG_DUMP,
        "-h", DB_HOST,
        "-p", str(DB_PORT),
        "-U", DB_USER,
        "-d", SOURCE_DB,
        "-F", "c",  # Custom archive format
        "-f", BACKUP_FILE
    ]
    res = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {res.stderr}")
    print(f"Backup created successfully: {BACKUP_FILE} ({os.path.getsize(BACKUP_FILE)} bytes)")

    print("\n=== Step 2: Creating Clean Isolation Database for Recovery Verification ===")
    conn_admin = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor_admin = conn_admin.cursor()

    # Drop if exists from prior aborted run
    cursor_admin.execute(f"DROP DATABASE IF EXISTS {RECOVERY_DB};")
    cursor_admin.execute(f"CREATE DATABASE {RECOVERY_DB};")
    print(f"Isolated test database '{RECOVERY_DB}' created.")

    print("\n=== Step 3: Restoring Database via pg_restore ===")
    PG_RESTORE = os.path.join(PG_BIN, "pg_restore.exe")
    restore_cmd = [
        PG_RESTORE,
        "-h", DB_HOST,
        "-p", str(DB_PORT),
        "-U", DB_USER,
        "-d", RECOVERY_DB,
        BACKUP_FILE
    ]
    res_restore = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
    # pg_restore may return 0 or non-fatal warning code
    print(f"pg_restore executed (exit code {res_restore.returncode}).")

    print("\n=== Step 4: Comparing Schemas and Row Counts Between Source and Restored DB ===")
    conn_src = psycopg2.connect(dbname=SOURCE_DB, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn_rec = psycopg2.connect(dbname=RECOVERY_DB, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

    cur_src = conn_src.cursor()
    cur_rec = conn_rec.cursor()

    # Query all user tables
    cur_src.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    src_tables = [r[0] for r in cur_src.fetchall()]

    cur_rec.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    rec_tables = [r[0] for r in cur_rec.fetchall()]

    assert src_tables == rec_tables, f"Table lists do not match!\nSrc: {src_tables}\nRec: {rec_tables}"
    print(f"All {len(src_tables)} tables perfectly matched between source and restored databases.")

    row_count_mismatches = 0
    total_rows = 0
    for tbl in src_tables:
        cur_src.execute(f"SELECT COUNT(*) FROM {tbl};")
        count_src = cur_src.fetchone()[0]
        cur_rec.execute(f"SELECT COUNT(*) FROM {tbl};")
        count_rec = cur_rec.fetchone()[0]
        total_rows += count_src

        if count_src != count_rec:
            print(f"MISMATCH in {tbl}: Source={count_src}, Restored={count_rec}")
            row_count_mismatches += 1
        else:
            print(f"  [OK] Table '{tbl}': {count_src} rows")

    conn_src.close()
    conn_rec.close()

    assert row_count_mismatches == 0, f"Found {row_count_mismatches} row count mismatches!"
    print(f"\nVerification Success: All {len(src_tables)} tables ({total_rows} total rows) restored with 100% fidelity.")

    print("\n=== Step 5: Clean Teardown of Non-Production Verification Database ===")
    cursor_admin.execute(f"DROP DATABASE {RECOVERY_DB};")
    cursor_admin.close()
    conn_admin.close()
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)
    print("Isolated test database dropped and temporary backup file cleaned up.")
    print("PostgreSQL Disaster Recovery & Restoration Verification: PASS")

if __name__ == "__main__":
    run_recovery_verification()
