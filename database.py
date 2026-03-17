# database.py
# Gujarat Domestic Worker Registration System
# SQLite database setup and all data functions
# Compliant with DPDP Act 2023 — raw Aadhaar numbers are never stored

import sqlite3
import hashlib
import uuid
import json
from datetime import datetime, date
from typing import Optional

DB_PATH = "gujarat_workers.db"


# ─────────────────────────────────────────────
# PRIVACY UTILITIES (DPDP Act 2023 & UIDAI)
# ─────────────────────────────────────────────

def hash_aadhaar(aadhaar_number: str) -> str:
    """
    UIDAI compliance: Never store raw Aadhaar numbers.
    Store only a one-way SHA-256 hash.
    """
    cleaned = aadhaar_number.replace(" ", "").strip()
    return hashlib.sha256(cleaned.encode()).hexdigest()


def mask_aadhaar(aadhaar_number: str) -> str:
    """
    Display-safe: show only last 4 digits.
    e.g., "XXXX XXXX 9012"
    """
    cleaned = aadhaar_number.replace(" ", "").strip()
    if len(cleaned) >= 4:
        return f"XXXX XXXX {cleaned[-4:]}"
    return "XXXX XXXX XXXX"


def generate_ref_id() -> str:
    """Generate a unique Gujarat registration reference ID."""
    short = str(uuid.uuid4()).upper()[:8]
    return f"GJ-{datetime.now().year}-{short}"


# ─────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────

def init_db():
    """
    Create all tables if they don't exist.
    Call this once at app startup.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Workers table
    # Note: aadhaar_hash stores SHA-256 hash, aadhaar_masked for display only
    c.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_id          TEXT UNIQUE NOT NULL,
            full_name       TEXT NOT NULL,
            date_of_birth   TEXT NOT NULL,
            gender          TEXT,
            aadhaar_hash    TEXT NOT NULL,
            aadhaar_masked  TEXT NOT NULL,
            phone           TEXT,
            address         TEXT,
            language        TEXT DEFAULT 'Gujarati',
            status          TEXT DEFAULT 'Pending',
            ai_risk_score   TEXT DEFAULT 'Low',
            ai_notes        TEXT,
            officer_id      TEXT,
            rejection_reason TEXT,
            employer_id     INTEGER,
            consent_given   INTEGER DEFAULT 1,
            submitted_at    TEXT NOT NULL,
            verified_at     TEXT,
            FOREIGN KEY (employer_id) REFERENCES employers(id)
        )
    """)

    # Employers table
    c.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name   TEXT NOT NULL,
            owner_name      TEXT NOT NULL,
            gst_number      TEXT,
            phone           TEXT,
            address         TEXT,
            registered_at   TEXT NOT NULL
        )
    """)

    # Holidays / Leave log table
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_ref_id   TEXT NOT NULL,
            leave_date      TEXT NOT NULL,
            reason          TEXT,
            employer_notified INTEGER DEFAULT 0,
            logged_at       TEXT NOT NULL,
            FOREIGN KEY (worker_ref_id) REFERENCES workers(ref_id)
        )
    """)

    # Audit log table — every action timestamped
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            action          TEXT NOT NULL,
            worker_ref_id   TEXT,
            performed_by    TEXT,
            details         TEXT,
            performed_at    TEXT NOT NULL
        )
    """)

    # Extra work requests table
    c.execute("""
        CREATE TABLE IF NOT EXISTS work_requests (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_ref_id   TEXT NOT NULL,
            employer_id     INTEGER NOT NULL,
            request_date    TEXT NOT NULL,
            extra_hours     REAL NOT NULL,
            reason          TEXT,
            status          TEXT DEFAULT 'Pending',
            requested_at    TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed mock data if tables are empty
    _seed_mock_data(conn)

    conn.close()


def _seed_mock_data(conn):
    """Add realistic mock data for the demo."""
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM employers")
    if c.fetchone()[0] > 0:
        return  # Already seeded

    # Seed Employers
    employers = [
        ("Patel Residence", "Mahesh Patel", "24AAACP1234F1ZY", "9876543210",
         "42, Satellite Road, Ahmedabad", "2024-01-15"),
        ("Shah Family", "Priya Shah", "24BBBCP5678G2ZY", "9876543211",
         "15, Navrangpura, Ahmedabad", "2024-02-20"),
        ("Desai Household", "Ravi Desai", "24CCCCP9012H3ZY", "9876543212",
         "8, Maninagar, Ahmedabad", "2024-03-10"),
    ]
    c.executemany(
        "INSERT INTO employers (business_name, owner_name, gst_number, phone, address, registered_at) VALUES (?,?,?,?,?,?)",
        employers
    )

    now = datetime.now().isoformat()

    # Seed Workers — mix of statuses to demonstrate all dashboard states
    workers = [
        # (ref_id, full_name, dob, gender, aadhaar_hash, aadhaar_masked,
        #  phone, address, language, status, ai_risk_score, ai_notes,
        #  officer_id, rejection_reason, employer_id, submitted_at, verified_at)
        (
            "GJ-2025-DEMO001", "Kamla Bai", "01/06/1985", "Female",
            hash_aadhaar("234567890123"), mask_aadhaar("234567890123"),
            "9012345678", "Vatva, Ahmedabad", "Gujarati",
            "Verified", "Low",
            "Age valid · Aadhaar format correct · No anomalies detected",
            "OFF-001", None, 1,
            "2025-01-10T10:00:00", "2025-01-12T14:30:00"
        ),
        (
            "GJ-2025-DEMO002", "Sunita Yadav", "15/03/1990", "Female",
            hash_aadhaar("345678901234"), mask_aadhaar("345678901234"),
            "9023456789", "Naroda, Ahmedabad", "Hindi",
            "Verified", "Low",
            "Age valid · Aadhaar format correct · No anomalies detected",
            "OFF-001", None, 2,
            "2025-01-15T09:00:00", "2025-01-16T11:00:00"
        ),
        (
            "GJ-2025-DEMO003", "Meena Parmar", "22/11/1978", "Female",
            hash_aadhaar("456789012345"), mask_aadhaar("456789012345"),
            "9034567890", "Gota, Ahmedabad", "Gujarati",
            "Pending", "Low",
            "Age valid · Aadhaar format correct · Awaiting officer review",
            None, None, 3,
            "2025-01-20T08:30:00", None
        ),
        (
            "GJ-2025-DEMO004", "Raju Kumar", "05/08/2008", "Male",
            hash_aadhaar("567890123456"), mask_aadhaar("567890123456"),
            "9045678901", "Bapunagar, Ahmedabad", "Hindi",
            "Pending", "High",
            "⚠️ AGE ALERT: DOB suggests applicant may be under 18. Manual verification required. Child Labour Act 2016 applies.",
            None, None, None,
            "2025-01-21T11:00:00", None
        ),
        (
            "GJ-2025-DEMO005", "Geeta Solanki", "30/04/1982", "Female",
            hash_aadhaar("678901234567"), mask_aadhaar("678901234567"),
            "9056789012", "Chandkheda, Ahmedabad", "Gujarati",
            "Rejected", "Medium",
            "Aadhaar number format inconsistency detected. Cross-check recommended.",
            "OFF-002",
            "Aadhaar verification failed — number format invalid. Please visit nearest Aadhaar enrollment centre.",
            None,
            "2025-01-18T14:00:00", "2025-01-19T10:00:00"
        ),
    ]

    c.executemany(
        """INSERT INTO workers
        (ref_id, full_name, date_of_birth, gender, aadhaar_hash, aadhaar_masked,
         phone, address, language, status, ai_risk_score, ai_notes,
         officer_id, rejection_reason, employer_id, submitted_at, verified_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        workers
    )

    # Seed some leaves
    leaves = [
        ("GJ-2025-DEMO001", "2025-02-01", "Makarsankranti festival", 1, now),
        ("GJ-2025-DEMO001", "2025-02-14", "Family function", 1, now),
        ("GJ-2025-DEMO002", "2025-02-05", "Doctor appointment", 1, now),
    ]
    c.executemany(
        "INSERT INTO leaves (worker_ref_id, leave_date, reason, employer_notified, logged_at) VALUES (?,?,?,?,?)",
        leaves
    )

    # Seed audit log
    audit_entries = [
        ("APPROVE", "GJ-2025-DEMO001", "OFF-001", "Worker approved after document verification", "2025-01-12T14:30:00"),
        ("APPROVE", "GJ-2025-DEMO002", "OFF-001", "Worker approved after document verification", "2025-01-16T11:00:00"),
        ("REJECT", "GJ-2025-DEMO005", "OFF-002", "Aadhaar format inconsistency", "2025-01-19T10:00:00"),
    ]
    c.executemany(
        "INSERT INTO audit_log (action, worker_ref_id, performed_by, details, performed_at) VALUES (?,?,?,?,?)",
        audit_entries
    )

    conn.commit()


# ─────────────────────────────────────────────
# WORKER CRUD FUNCTIONS
# ─────────────────────────────────────────────

def add_worker(
    full_name: str,
    date_of_birth: str,
    gender: str,
    aadhaar_number: str,    # Raw number — will be hashed immediately
    phone: str,
    address: str,
    language: str,
    ai_risk_score: str,
    ai_notes: str,
) -> str:
    """
    Insert a new worker registration.
    Returns the generated ref_id.
    DPDP compliance: aadhaar_number is hashed before storage.
    """
    ref_id = generate_ref_id()
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO workers
        (ref_id, full_name, date_of_birth, gender, aadhaar_hash, aadhaar_masked,
         phone, address, language, status, ai_risk_score, ai_notes,
         consent_given, submitted_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ref_id, full_name, date_of_birth, gender,
        hash_aadhaar(aadhaar_number),      # ← hash stored, not raw
        mask_aadhaar(aadhaar_number),      # ← masked for display
        phone, address, language,
        "Pending", ai_risk_score, ai_notes,
        1, now
    ))

    # Audit log
    c.execute("""
        INSERT INTO audit_log (action, worker_ref_id, performed_by, details, performed_at)
        VALUES (?,?,?,?,?)
    """, ("REGISTER", ref_id, "WORKER_SELF", f"New registration: {full_name}", now))

    conn.commit()
    conn.close()

    # DPDP Act 2023: raw aadhaar_number is NOT stored — garbage collected here
    del aadhaar_number

    return ref_id


def get_all_workers(status_filter: Optional[str] = None):
    """
    Return all workers, optionally filtered by status.
    status_filter: 'Pending', 'Verified', 'Rejected', or None for all
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if status_filter:
        c.execute(
            "SELECT * FROM workers WHERE status = ? ORDER BY submitted_at DESC",
            (status_filter,)
        )
    else:
        c.execute("SELECT * FROM workers ORDER BY submitted_at DESC")

    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_worker_by_ref(ref_id: str) -> Optional[dict]:
    """Get a single worker by their reference ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM workers WHERE ref_id = ?", (ref_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def approve_worker(ref_id: str, officer_id: str) -> bool:
    """
    Approve a worker registration.
    Human-in-loop mandate: officer_id MUST be provided.
    Returns True on success.
    """
    # Human-in-loop mandate — officer ID required
    assert officer_id and officer_id.strip(), \
        "COMPLIANCE ERROR: Officer ID required for approval. AI cannot auto-approve."

    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE workers
        SET status = 'Verified', officer_id = ?, verified_at = ?
        WHERE ref_id = ? AND status = 'Pending'
    """, (officer_id, now, ref_id))

    rows_affected = c.rowcount

    if rows_affected > 0:
        c.execute("""
            INSERT INTO audit_log (action, worker_ref_id, performed_by, details, performed_at)
            VALUES (?,?,?,?,?)
        """, ("APPROVE", ref_id, officer_id, "Worker registration approved", now))

    conn.commit()
    conn.close()
    return rows_affected > 0


def reject_worker(ref_id: str, officer_id: str, reason: str) -> bool:
    """
    Reject a worker registration with a reason.
    Human-in-loop mandate: officer_id MUST be provided.
    """
    assert officer_id and officer_id.strip(), \
        "COMPLIANCE ERROR: Officer ID required for rejection. AI cannot auto-reject."
    assert reason and reason.strip(), \
        "Rejection reason is required by law."

    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE workers
        SET status = 'Rejected', officer_id = ?, rejection_reason = ?, verified_at = ?
        WHERE ref_id = ? AND status = 'Pending'
    """, (officer_id, reason, now, ref_id))

    rows_affected = c.rowcount

    if rows_affected > 0:
        c.execute("""
            INSERT INTO audit_log (action, worker_ref_id, performed_by, details, performed_at)
            VALUES (?,?,?,?,?)
        """, ("REJECT", ref_id, officer_id, f"Rejected: {reason}", now))

    conn.commit()
    conn.close()
    return rows_affected > 0


def get_dashboard_stats() -> dict:
    """Return aggregate stats for the admin dashboard metrics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM workers")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM workers WHERE status = 'Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM workers WHERE status = 'Verified'")
    approved = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM workers WHERE status = 'Rejected'")
    rejected = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM workers WHERE ai_risk_score = 'High'")
    high_risk = c.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "high_risk": high_risk,
    }


# ─────────────────────────────────────────────
# EMPLOYER FUNCTIONS
# ─────────────────────────────────────────────

def get_all_employers():
    """Return all employers."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employers ORDER BY business_name")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_workers_for_employer(employer_id: int):
    """Return all verified workers mapped to an employer."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM workers WHERE employer_id = ? ORDER BY full_name",
        (employer_id,)
    )
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def add_work_request(worker_ref_id: str, employer_id: int,
                     request_date: str, extra_hours: float, reason: str) -> dict:
    """
    Add an extra work hours request.
    Labour Code 2020 compliance: max 9 hrs/day, 48 hrs/week.
    Returns {"allowed": bool, "message": str}
    """
    # Labour Code 2020 check
    if extra_hours > 4:  # extra hours on top of regular 8 = 12 total — reject
        return {
            "allowed": False,
            "message": "Exceeds Labour Code 2020 limit: maximum 1-4 extra hours per request (total max 9hrs/day)"
        }

    # Check weekly hours for this worker
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(SUM(extra_hours), 0) FROM work_requests
        WHERE worker_ref_id = ?
        AND strftime('%W', request_date) = strftime('%W', ?)
        AND status != 'Rejected'
    """, (worker_ref_id, request_date))
    weekly_extra = c.fetchone()[0]

    # Regular hours (8/day × 5 days = 40) + extra already approved this week
    if weekly_extra + extra_hours + 40 > 48:
        conn.close()
        return {
            "allowed": False,
            "message": f"Weekly limit exceeded: {48 - 40 - weekly_extra:.1f} extra hours remaining this week (Labour Code 2020)"
        }

    now = datetime.now().isoformat()
    c.execute("""
        INSERT INTO work_requests
        (worker_ref_id, employer_id, request_date, extra_hours, reason, status, requested_at)
        VALUES (?,?,?,?,?,?,?)
    """, (worker_ref_id, employer_id, request_date, extra_hours, reason, "Pending", now))
    conn.commit()
    conn.close()

    return {"allowed": True, "message": "Request sent to worker"}


# ─────────────────────────────────────────────
# LEAVE FUNCTIONS
# ─────────────────────────────────────────────

def log_leave(worker_ref_id: str, leave_date: str,
              reason: str, notify_employer: bool) -> bool:
    """Log a worker's leave/holiday."""
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO leaves (worker_ref_id, leave_date, reason, employer_notified, logged_at)
        VALUES (?,?,?,?,?)
    """, (worker_ref_id, leave_date, reason, int(notify_employer), now))

    # Audit
    c.execute("""
        INSERT INTO audit_log (action, worker_ref_id, performed_by, details, performed_at)
        VALUES (?,?,?,?,?)
    """, ("LEAVE_LOG", worker_ref_id, "WORKER_SELF", f"Leave on {leave_date}: {reason}", now))

    conn.commit()
    conn.close()
    return True


def get_leaves_for_worker(worker_ref_id: str):
    """Get all leaves for a worker, most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM leaves WHERE worker_ref_id = ? ORDER BY leave_date DESC",
        (worker_ref_id,)
    )
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


# ─────────────────────────────────────────────
# AUDIT LOG FUNCTIONS
# ─────────────────────────────────────────────

def get_recent_audit_log(limit: int = 20):
    """Return the most recent audit log entries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM audit_log ORDER BY performed_at DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows
