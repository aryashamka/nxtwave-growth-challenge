"""
Vercel Serverless Entrypoint (Flask API)
Handles all growth engine endpoints on Vercel's serverless Python runtime.
"""

import os
import sys
import json
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_db, register_user, get_user, get_referral_count,
    get_top_referrers, get_college_leaderboard, get_growth_kpis,
    db_session
)
from ai_recommender import generate_project_idea, PROJECT_KNOWLEDGE_BASE
from bot import process_bot_action, format_welcome_message, format_registration_pass
from seed_data import populate_simulation_data

app = Flask(__name__, static_folder="../public", static_url_path="")

# Determine DB path (Vercel serverless requires /tmp for write access)
IS_VERCEL = bool(os.getenv("VERCEL"))
VERCEL_DB = "/tmp/growth_data.db" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "..", "growth_data.db")

def ensure_initialized():
    """Initializes and seeds DB if running in a fresh Vercel serverless container."""
    if not os.path.exists(VERCEL_DB):
        populate_simulation_data(target_count=438, db_path=VERCEL_DB)

@app.route("/api/kpis", methods=["GET"])
def api_kpis():
    ensure_initialized()
    kpis = get_growth_kpis(db_path=VERCEL_DB)
    return jsonify(kpis)

@app.route("/api/timeline", methods=["GET"])
def api_timeline():
    ensure_initialized()
    with db_session(VERCEL_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(registered_at) as reg_date,
                   COUNT(*) as daily_count,
                   SUM(CASE WHEN referred_by IS NOT NULL THEN 1 ELSE 0 END) as viral_count,
                   SUM(CASE WHEN referred_by IS NULL THEN 1 ELSE 0 END) as direct_count
            FROM users
            GROUP BY DATE(registered_at)
            ORDER BY reg_date ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
    return jsonify(rows)

@app.route("/api/leaderboards", methods=["GET"])
def api_leaderboards():
    ensure_initialized()
    top_students = get_top_referrers(10, db_path=VERCEL_DB)
    top_colleges = get_college_leaderboard(10, db_path=VERCEL_DB)
    return jsonify({
        "students": top_students,
        "colleges": top_colleges
    })

@app.route("/api/register", methods=["POST"])
def api_register():
    ensure_initialized()
    data = request.json or {}
    sim_id = data.get("user_id") or f"tg_{abs(hash(data.get('name', 'student'))) % 100000}"
    resp = process_bot_action("register", {
        "user_id": sim_id,
        "name": data.get("name", "Student"),
        "college": data.get("college", "Other College"),
        "branch": data.get("branch", "Computer Science & Engineering (CSE)"),
        "referred_by": data.get("referred_by") or None,
        "channel": "Vercel Web Simulator"
    })
    return jsonify(resp)

@app.route("/api/ideas", methods=["POST"])
def api_ideas():
    data = request.json or {}
    branch = data.get("branch", "Computer Science & Engineering (CSE)")
    name = data.get("name", "Student")
    res = generate_project_idea(branch, name)
    return jsonify(res)

@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Handler for Vercel WSGI
app.debug = False

if __name__ == "__main__":
    ensure_initialized()
    app.run(port=5000, debug=True)
