"""
NxtWave Growth Bot: Telegram Conversational Engine
Implements:
1. One-tap Telegram registration flow (zero tedious forms)
2. Unique referral link generation & viral loop tracking
3. Reward ladder progression (2, 5, 10 referrals)
4. Live college vs college leaderboard (/leaderboard)
5. AI project idea generator with resume bullets (/ideas)
6. Automated reminder notification simulation
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, Optional

from database import (
    register_user, get_user, get_referral_count,
    get_top_referrers, get_college_leaderboard, DB_PATH
)
from ai_recommender import generate_project_idea

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
BOT_USERNAME = "NxtWaveAIWorkshopBot"

def format_welcome_message(name: str, referrer_name: Optional[str] = None) -> str:
    ref_note = f"\n🎁 *Invited by your peer {referrer_name}!*\n" if referrer_name else ""
    return (
        f"🚀 *Hey {name}! Welcome to NxtWave's 60-Min AI Challenge.*{ref_note}\n\n"
        "Tired of generic CRUD apps on your resume that recruiters ignore?\n"
        "In this 60-minute live workshop, you will:\n"
        "✅ Build & deploy an autonomous AI Agent\n"
        "✅ Get 3 high-impact resume bullet points for 2025/2026 placements\n"
        "✅ Receive a verifiable NxtWave AI Builder Certificate\n\n"
        "👉 *Ready to lock in your free seat?* Let's set up your profile in 10 seconds!"
    )

def format_registration_pass(user: Dict, referral_count: int = 0) -> str:
    ref_code = user["referral_code"]
    ref_link = f"https://t.me/{BOT_USERNAME}?start={ref_code}"
    
    tier_progress = ""
    if referral_count >= 10:
        tier_progress = "🏆 *Tier 3 UNLOCKED:* VIP Pass + Live AI Project Code Review!"
    elif referral_count >= 5:
        tier_progress = "🔥 *Tier 2 UNLOCKED:* Full GitHub Template + 50 AI Interview Questions!"
    elif referral_count >= 2:
        tier_progress = "⭐ *Tier 1 UNLOCKED:* ATS Resume Bullet Points Pack!"
    else:
        tier_progress = f"🎯 *Referral Status:* {referral_count}/2 invites to unlock Tier 1 Reward Pack!"
        
    whatsapp_share_text = (
        f"Hey! I just registered for NxtWave's free 'Build Your First AI Project in 60 Minutes' workshop. "
        f"You build a real AI project for campus placements. Register free with my link to get the starter code: {ref_link}"
    )
    
    return (
        f"🎉 *CONGRATULATIONS {user['name'].upper()}!*\n"
        f"🎟 *Your Workshop Admit Pass is Confirmed!*\n\n"
        f"🏛 *College:* {user['college']}\n"
        f"💻 *Branch:* {user['branch']}\n"
        f"📅 *Date & Time:* Saturday, 6:00 PM IST (Online)\n"
        f"🔗 *Your Unique Referral Link:*\n`{ref_link}`\n\n"
        f"{tier_progress}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎁 *REWARD LADDER (Invite Batchmates):*\n"
        f"• *2 Referrals:* AI Resume Bullet Points (ATS Optimized)\n"
        f"• *5 Referrals:* Complete GitHub Starter Repository\n"
        f"• *10 Referrals:* Top 1% VIP Certificate & Live Code Review\n\n"
        f"📱 *Tap to copy WhatsApp share text:*\n_{whatsapp_share_text}_\n\n"
        f"💡 Type /ideas to get a custom project idea for {user['branch']}!\n"
        f"🏆 Type /leaderboard to see your college ranking!"
    )

def format_leaderboard() -> str:
    top_students = get_top_referrers(5)
    top_colleges = get_college_leaderboard(5)
    
    msg = "🏆 *LIVE GROWTH LEADERBOARD*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "🔥 *TOP STUDENT ADVOCATES:*\n"
    for i, s in enumerate(top_students, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "▫️"
        msg += f"{medal} *{s['name']}* ({s['college']}) — `{s['referral_count']} invites`\n"
        
    msg += "\n🏛 *COLLEGE VS COLLEGE STANDINGS:*\n"
    for i, c in enumerate(top_colleges, 1):
        flag = "👑" if i == 1 else f"{i}."
        msg += f"{flag} *{c['college']}*: `{c['total_registrations']} students registered`\n"
        
    msg += "\n⚡ *Want to push your college to #1? Share your referral link with batch WhatsApp groups!*"
    return msg

def format_reminder(user_name: str, hours_left: int = 24) -> str:
    return (
        f"⏰ *Reminder: Workshop starts in {hours_left} Hours!* ⏰\n\n"
        f"Hey {user_name}, get your laptop and code editor ready!\n"
        f"In 60 minutes, you will build and deploy your first live AI project.\n\n"
        f"📍 *Meeting Link:* `https://meet.nxtwave.in/ai-workshop-live`\n"
        f"📋 *Checklist before joining:*\n"
        f"1. Have Python 3.10+ installed or open Google Colab\n"
        f"2. Bring 1 batchmate so you can peer-code together\n\n"
        f"See you live at 6:00 PM!"
    )

def process_bot_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core state machine dispatcher. Used by both the Telegram polling service
    and the interactive Streamlit Web Simulator.
    """
    user_id = str(payload.get("user_id", "demo_user"))
    user_name = payload.get("name", "Student")
    
    if action == "start":
        ref_code = payload.get("ref_code")
        user = get_user(user_id)
        if user:
            ref_count = get_referral_count(user["referral_code"])
            return {
                "status": "already_registered",
                "message": format_registration_pass(user, ref_count),
                "user": user
            }
        return {
            "status": "need_details",
            "message": format_welcome_message(user_name, ref_code),
            "ref_code": ref_code
        }
        
    elif action == "register":
        is_new, msg, user = register_user(
            user_id=user_id,
            name=user_name,
            username=payload.get("username", ""),
            college=payload.get("college", "Other College"),
            branch=payload.get("branch", "Computer Science & Engineering (CSE)"),
            year="Final Year (2025)",
            referred_by=payload.get("referred_by"),
            channel=payload.get("channel", "Telegram Direct")
        )
        ref_count = get_referral_count(user["referral_code"])
        return {
            "status": "success" if is_new else "existing",
            "message": format_registration_pass(user, ref_count),
            "user": user
        }
        
    elif action == "leaderboard":
        return {
            "status": "ok",
            "message": format_leaderboard()
        }
        
    elif action == "ideas":
        user = get_user(user_id)
        branch = user["branch"] if user else payload.get("branch", "Computer Science & Engineering (CSE)")
        idea = generate_project_idea(branch, user_name)
        return {
            "status": "ok",
            "message": idea["formatted_text"],
            "raw_idea": idea
        }
        
    elif action == "reminder":
        return {
            "status": "ok",
            "message": format_reminder(user_name, payload.get("hours_left", 24))
        }
        
    return {"status": "error", "message": "Unknown action"}

def run_telegram_poller():
    """Production long-polling loop for live Telegram deployment."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[!] Warning: TELEGRAM_BOT_TOKEN not set. Set it in environment to run live bot.")
        print("[!] You can test the bot live via the Streamlit simulator: streamlit run dashboard.py")
        return
        
    print(f"[*] Starting Telegram long-polling on @{BOT_USERNAME}...")
    offset = None
    while True:
        try:
            params = {"timeout": 30, "offset": offset}
            res = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
            if res.status_code == 200:
                data = res.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    text = message.get("text", "")
                    chat_id = message.get("chat", {}).get("id")
                    from_user = message.get("from", {})
                    user_id = str(from_user.get("id"))
                    first_name = from_user.get("first_name", "Student")
                    username = from_user.get("username", "")
                    
                    if text.startswith("/start"):
                        parts = text.split()
                        ref_code = parts[1].replace("ref_", "") if len(parts) > 1 else None
                        resp = process_bot_action("start", {
                            "user_id": user_id,
                            "name": first_name,
                            "ref_code": ref_code
                        })
                        requests.post(f"{BASE_URL}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": resp["message"],
                            "parse_mode": "Markdown"
                        })
                    elif text == "/leaderboard":
                        resp = process_bot_action("leaderboard", {})
                        requests.post(f"{BASE_URL}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": resp["message"],
                            "parse_mode": "Markdown"
                        })
                    elif text == "/ideas":
                        resp = process_bot_action("ideas", {"user_id": user_id, "name": first_name})
                        requests.post(f"{BASE_URL}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": resp["message"],
                            "parse_mode": "Markdown"
                        })
            time.sleep(1)
        except Exception as e:
            print(f"[!] Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_telegram_poller()
