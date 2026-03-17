# auth.py
# Authentication module — OTP login for Admin and Employer
# Demo mode: OTP shown on screen (no real SMS needed)
# Production mode: plug in Fast2SMS / MSG91 / Twilio

import sqlite3
import random
import hashlib
import string
from datetime import datetime, timedelta

DB_PATH = "gujarat_workers.db"


# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def init_auth_tables():
    """Create users and otp_store tables. Call once at startup."""
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            phone        TEXT UNIQUE NOT NULL,
            name         TEXT NOT NULL,
            role         TEXT NOT NULL,
            is_active    INTEGER DEFAULT 1,
            created_at   TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS otp_store (
            phone        TEXT PRIMARY KEY,
            otp_hash     TEXT NOT NULL,
            expires_at   TEXT NOT NULL,
            attempts     INTEGER DEFAULT 0
        )
    """)

    # Seed demo accounts if not already present
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now   = datetime.now().isoformat()
        demos = [
            ("9000000001", "Officer Rajesh Patel",  "admin",    1, now),
            ("9000000002", "Officer Priya Shah",    "admin",    1, now),
            ("9000000003", "Mahesh Patel (Employer)","employer", 1, now),
            ("9000000004", "Priya Shah (Employer)",  "employer", 1, now),
        ]
        c.executemany(
            "INSERT INTO users (phone, name, role, is_active, created_at) VALUES (?,?,?,?,?)",
            demos
        )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# OTP UTILITIES
# ─────────────────────────────────────────────

def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def generate_otp(phone: str) -> tuple[str, bool]:
    """
    Generate a 6-digit OTP and store its hash in the database.
    Returns (otp_code, is_registered_user).
    OTP expires in 10 minutes.
    """
    otp        = "".join(random.choices(string.digits, k=6))
    otp_hash   = _hash_otp(otp)
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # Check if phone is registered
    c.execute("SELECT id FROM users WHERE phone = ? AND is_active = 1", (phone,))
    is_registered = c.fetchone() is not None

    # Store OTP (replace if exists)
    c.execute("""
        INSERT INTO otp_store (phone, otp_hash, expires_at, attempts)
        VALUES (?, ?, ?, 0)
        ON CONFLICT(phone) DO UPDATE SET
            otp_hash   = excluded.otp_hash,
            expires_at = excluded.expires_at,
            attempts   = 0
    """, (phone, otp_hash, expires_at))

    conn.commit()
    conn.close()
    return otp, is_registered


def verify_otp(phone: str, entered_otp: str) -> dict:
    """
    Verify an OTP.
    Returns {"success": bool, "message": str, "user": dict|None}
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c    = conn.cursor()

    c.execute("SELECT * FROM otp_store WHERE phone = ?", (phone,))
    record = c.fetchone()

    if not record:
        conn.close()
        return {"success": False, "message": "No OTP found. Please request a new one.", "user": None}

    # Check attempts (max 3)
    if record["attempts"] >= 3:
        conn.close()
        return {"success": False, "message": "Too many attempts. Please request a new OTP.", "user": None}

    # Check expiry
    expires_at = datetime.fromisoformat(record["expires_at"])
    if datetime.now() > expires_at:
        conn.close()
        return {"success": False, "message": "OTP expired. Please request a new one.", "user": None}

    # Increment attempts
    c.execute("UPDATE otp_store SET attempts = attempts + 1 WHERE phone = ?", (phone,))
    conn.commit()

    # Verify hash
    if _hash_otp(entered_otp.strip()) != record["otp_hash"]:
        remaining = 3 - (record["attempts"] + 1)
        conn.close()
        return {"success": False,
                "message": f"Incorrect OTP. {remaining} attempt(s) remaining.",
                "user": None}

    # OTP correct — fetch user
    c.execute("SELECT * FROM users WHERE phone = ? AND is_active = 1", (phone,))
    user_row = c.fetchone()

    # Clear used OTP
    c.execute("DELETE FROM otp_store WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

    if not user_row:
        return {"success": False,
                "message": "Phone number not registered. Contact Gujarat Labour Department.",
                "user": None}

    user = dict(user_row)
    return {"success": True, "message": f"Welcome, {user['name']}!", "user": user}


# ─────────────────────────────────────────────
# SIGNUP — register a new admin or employer
# ─────────────────────────────────────────────

def register_user(phone: str, name: str, role: str) -> dict:
    """
    Register a new user (admin or employer).
    Returns {"success": bool, "message": str}
    Admin accounts require manual approval in real deployment.
    """
    if role not in ("admin", "employer"):
        return {"success": False, "message": "Invalid role. Must be admin or employer."}

    if len(phone) != 10 or not phone.isdigit():
        return {"success": False, "message": "Phone must be 10 digits."}

    if len(name.strip()) < 3:
        return {"success": False, "message": "Name must be at least 3 characters."}

    now  = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (phone, name, role, is_active, created_at) VALUES (?,?,?,?,?)",
            (phone, name.strip(), role, 1, now)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Account created for {name}. You can now log in."}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "This phone number is already registered."}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_user_by_phone(phone: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c    = conn.cursor()
    c.execute("SELECT * FROM users WHERE phone = ? AND is_active = 1", (phone,))
    row  = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c    = conn.cursor()
    c.execute("SELECT id, phone, name, role, is_active, created_at FROM users ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def send_otp_sms(phone: str, otp: str) -> bool:
    """
    Production SMS hook — plug in Fast2SMS / MSG91 / Twilio here.
    Demo mode: always returns False (OTP shown on screen instead).
    
    To enable real SMS (Fast2SMS example):
        import requests
        resp = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": YOUR_FAST2SMS_KEY},
            data={"variables_values": otp, "route": "otp", "numbers": phone}
        )
        return resp.json().get("return", False)
    """
    return False   # Demo mode — show OTP on screen