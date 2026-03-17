# check_db.py
# Run this file to verify your entire database is working correctly
# Command: python check_db.py

import sqlite3
import database as db

db.init_db()

print("=" * 60)
print("GUJARAT WORKER SYSTEM — DATABASE VERIFICATION REPORT")
print("=" * 60)

# ── Check 1: All Workers ──
print("\n📋 CHECK 1: ALL WORKERS")
print("-" * 60)
workers = db.get_all_workers()
for w in workers:
    print(f"  {w['ref_id']} | {w['full_name']:<20} | {w['status']:<10} | Risk: {w['ai_risk_score']}")

# ── Check 2: DPDP Compliance ──
print("\n🔒 CHECK 2: DPDP COMPLIANCE (Aadhaar never stored raw)")
print("-" * 60)
conn = sqlite3.connect('gujarat_workers.db')
c = conn.cursor()
c.execute("SELECT full_name, aadhaar_hash, aadhaar_masked FROM workers")
for row in c.fetchall():
    hash_len = len(row[1])
    status = "PASS" if hash_len == 64 else "FAIL"
    print(f"  [{status}] {row[0]:<20} | Hash: {hash_len} chars | Display: {row[2]}")

# ── Check 3: Table Counts ──
print("\n📊 CHECK 3: TABLE RECORD COUNTS")
print("-" * 60)
for table in ['workers', 'employers', 'leaves', 'audit_log', 'work_requests']:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"  {table:<20}: {count} records")

# ── Check 4: Audit Log ──
print("\n📝 CHECK 4: RECENT AUDIT LOG")
print("-" * 60)
audit = db.get_recent_audit_log(limit=10)
for a in audit:
    print(f"  {a['action']:<12} | {a.get('worker_ref_id','—'):<22} | by {a.get('performed_by','—'):<12} | {a['performed_at'][:16]}")

# ── Check 5: Dashboard Stats ──
print("\n📈 CHECK 5: DASHBOARD STATISTICS")
print("-" * 60)
stats = db.get_dashboard_stats()
print(f"  Total Registered : {stats['total']}")
print(f"  Pending          : {stats['pending']}")
print(f"  Approved         : {stats['approved']}")
print(f"  Rejected         : {stats['rejected']}")
print(f"  High Risk Flags  : {stats['high_risk']}")

# ── Check 6: Employers ──
print("\n🏢 CHECK 6: EMPLOYERS")
print("-" * 60)
employers = db.get_all_employers()
for e in employers:
    print(f"  {e['id']} | {e['business_name']:<25} | {e['owner_name']}")

conn.close()

print("\n" + "=" * 60)
print("ALL CHECKS COMPLETE")
print("=" * 60)