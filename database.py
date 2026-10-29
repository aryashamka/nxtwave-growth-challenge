"""
NxtWave Growth Engine Database Layer
Handles registration persistence, referral chain tracking, college leaderboards,
and viral growth analytics with proper connection lifecycle management.
"""

import sqlite3
import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

DB_PATH = "growth_data.db"

@contextmanager
def db_session(db_path: str = DB_PATH):
    """Context manager that guarantees connection closure on Windows."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    """Initializes tables and indexes for high-speed referral queries."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT,
                college TEXT NOT NULL,
                branch TEXT NOT NULL,
                year TEXT NOT NULL,
                referral_code TEXT UNIQUE NOT NULL,
                referred_by TEXT,
                channel TEXT DEFAULT 'Direct',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_opt_in BOOLEAN DEFAULT 1,
                unlocked_tier INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_referred_by 
            ON users(referred_by)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_college 
            ON users(college)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_referral_code 
            ON users(referral_code)
        """)
        conn.commit()

def generate_unique_referral_code(cursor: sqlite3.Cursor, name: str, user_id: str) -> str:
    """Generates a guaranteed unique, clean referral code like 'RAHUL482'."""
    clean_name = "".join(ch for ch in name if ch.isalnum()).upper()[:6]
    if not clean_name:
        clean_name = "STUDENT"
    salt = abs(hash(str(user_id))) % 900 + 100
    candidate = f"{clean_name}{salt}"
    
    counter = 1
    while True:
        cursor.execute("SELECT 1 FROM users WHERE referral_code = ?", (candidate,))
        if not cursor.fetchone():
            return candidate
        candidate = f"{clean_name}{salt}_{counter}"
        counter += 1

def generate_referral_code(name: str, user_id: str) -> str:
    """Backward compatibility helper."""
    clean_name = "".join(ch for ch in name if ch.isalnum()).upper()[:6] or "STUDENT"
    salt = abs(hash(str(user_id))) % 900 + 100
    return f"{clean_name}{salt}"

def register_user(
    user_id: str,
    name: str,
    username: Optional[str] = "",
    college: str = "Unknown College",
    branch: str = "Computer Science & Engineering (CSE)",
    year: str = "Final Year (2025)",
    referred_by: Optional[str] = None,
    channel: str = "Telegram Bot",
    db_path: str = DB_PATH
) -> Tuple[bool, str, Dict]:
    """
    Registers a student. Prevents duplicate registrations.
    Tracks referrer and checks tier unlocks.
    """
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if already registered
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        existing = cursor.fetchone()
        if existing:
            return False, "You are already registered for the workshop!", dict(existing)
        
        # Validate referred_by code
        valid_referrer = None
        if referred_by:
            ref_clean = referred_by.strip().upper()
            cursor.execute("SELECT referral_code FROM users WHERE UPPER(referral_code) = ?", (ref_clean,))
            ref_match = cursor.fetchone()
            if ref_match:
                valid_referrer = ref_match["referral_code"]
        
        ref_code = generate_unique_referral_code(cursor, name, user_id)
        
        cursor.execute("""
            INSERT INTO users (user_id, name, username, college, branch, year, referral_code, referred_by, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(user_id), name, username or "", college, branch, year, ref_code, valid_referrer, channel))
        conn.commit()
        
    # Check if referrer unlocked any new rewards
    if valid_referrer:
        update_user_rewards(valid_referrer, db_path)
        
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        user_data = dict(cursor.fetchone())
        return True, "Registration successful!", user_data

def update_user_rewards(ref_code: str, db_path: str = DB_PATH):
    """Updates reward tier based on count of successful referrals."""
    count = get_referral_count(ref_code, db_path)
    tier = 0
    if count >= 10:
        tier = 3  # VIP Pass + Full AI Project Kit + Certificate Shoutout
    elif count >= 5:
        tier = 2  # GitHub Starter Templates + 50 AI Interview Questions
    elif count >= 2:
        tier = 1  # AI Project Resume Bullet Points Pack
    
    with db_session(db_path) as conn:
        conn.cursor().execute("UPDATE users SET unlocked_tier = ? WHERE referral_code = ?", (tier, ref_code))
        conn.commit()

def get_user(user_id: str, db_path: str = DB_PATH) -> Optional[Dict]:
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_referral_count(ref_code: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE referred_by = ?", (ref_code,))
        return cursor.fetchone()["count"]

def get_top_referrers(limit: int = 10, db_path: str = DB_PATH) -> List[Dict]:
    """Returns top student advocates driving growth."""
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.name, u.college, u.referral_code, COUNT(r.user_id) as referral_count, u.unlocked_tier
            FROM users u
            JOIN users r ON u.referral_code = r.referred_by
            GROUP BY u.referral_code
            ORDER BY referral_count DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_college_leaderboard(limit: int = 10, db_path: str = DB_PATH) -> List[Dict]:
    """Returns college vs college registration standings."""
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT college, COUNT(*) as total_registrations,
                   SUM(CASE WHEN referred_by IS NOT NULL THEN 1 ELSE 0 END) as viral_registrations
            FROM users
            GROUP BY college
            ORDER BY total_registrations DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_growth_kpis(db_path: str = DB_PATH) -> Dict:
    """Calculates all key growth metrics including K-Factor and pacing."""
    init_db(db_path)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as viral FROM users WHERE referred_by IS NOT NULL")
        viral = cursor.fetchone()["viral"]
        
        direct = total - viral
        k_factor = round(viral / direct, 2) if direct > 0 else 0.0
        
        cursor.execute("""
            SELECT branch, COUNT(*) as count 
            FROM users 
            GROUP BY branch 
            ORDER BY count DESC
        """)
        branches = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT channel, COUNT(*) as count 
            FROM users 
            GROUP BY channel 
            ORDER BY count DESC
        """)
        channels = [dict(row) for row in cursor.fetchall()]
        
        budget_spent = 1200
        cost_per_reg = round(budget_spent / total, 2) if total > 0 else 0.0
        
        return {
            "total_registrations": total,
            "target": 500,
            "progress_pct": round((total / 500) * 100, 1),
            "direct_registrations": direct,
            "viral_registrations": viral,
            "k_factor": k_factor,
            "branches": branches,
            "channels": channels,
            "cost_per_registration": cost_per_reg,
            "budget_spent": budget_spent,
            "budget_total": 2000
        }
