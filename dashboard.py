"""
NxtWave Growth Intern Challenge: Executive Growth Dashboard & Live Bot Simulator
Built with Streamlit.
Serves as the interactive working asset demo + real-time growth analytics command center.
"""

import streamlit as st
import pandas as pd
import datetime
import random
import sqlite3

from database import (
    get_connection, get_growth_kpis, get_top_referrers,
    get_college_leaderboard, register_user, get_user,
    get_referral_count, DB_PATH
)
from bot import process_bot_action, format_welcome_message, format_registration_pass
from ai_recommender import generate_project_idea, PROJECT_KNOWLEDGE_BASE

# Page configuration
st.set_page_config(
    page_title="NxtWave Growth Engine | 500 Registrations Sprint",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .kpi-val {
        font-size: 2rem;
        font-weight: 800;
        color: #2563EB;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .telegram-bubble {
        background-color: #F1F5F9;
        border-left: 4px solid #0284C7;
        padding: 14px 18px;
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin-bottom: 12px;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=45)
st.sidebar.title("NxtWave Growth Engine")
st.sidebar.markdown("**Campaign:** 60-Min AI Project Workshop")
st.sidebar.markdown("**Target:** 500 Final-Year Engineers")
st.sidebar.markdown("**Budget:** ₹2,000 | **Duration:** 7 Days")

nav_choice = st.sidebar.radio(
    "Select View:",
    ["📊 Executive Growth Dashboard", "🤖 Interactive Bot Simulator", "💡 AI Project Ideator (/ideas)", "📋 Growth Plan & Strategic Logic"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Key Insight:** ₹2,000 spent on Meta Ads gets only ~65 leads. "
    "This growth engine deploys ₹1,200 as Class Rep micro-bounties and leverages a Telegram viral loop to achieve 500+ registrations at **₹3.42/lead**."
)

# -------------------------------------------------------------
# VIEW 1: EXECUTIVE GROWTH DASHBOARD
# -------------------------------------------------------------
if nav_choice == "📊 Executive Growth Dashboard":
    st.markdown('<div class="main-header">📈 Live Campaign Performance Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time telemetry tracking registrations, viral K-factor, college race, and acquisition efficiency.</div>', unsafe_allow_html=True)
    
    kpis = get_growth_kpis()
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Registrations", f"{kpis['total_registrations']}", f"{kpis['progress_pct']}% of Goal")
    with col2:
        st.metric("Viral K-Factor", f"{kpis['k_factor']}", "Target: >0.25 (Viral Loop)")
    with col3:
        st.metric("Direct vs Viral Leads", f"{kpis['direct_registrations']} / {kpis['viral_registrations']}")
    with col4:
        st.metric("Cost Per Registration", f"₹{kpis['cost_per_registration']}", "Budget: ₹2,000")
    with col5:
        st.metric("Budget Utilized", f"₹{kpis['budget_spent']} / ₹2,000", f"₹{kpis['budget_total'] - kpis['budget_spent']} Reserve")
        
    st.markdown("---")
    
    # Growth Trajectory & Channel Attribution
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        st.subheader("📅 7-Day Cumulative Growth Velocity")
        with get_connection() as conn:
            df_time = pd.read_sql_query("""
                SELECT DATE(registered_at) as reg_date,
                       COUNT(*) as daily_count,
                       SUM(CASE WHEN referred_by IS NOT NULL THEN 1 ELSE 0 END) as viral_count,
                       SUM(CASE WHEN referred_by IS NULL THEN 1 ELSE 0 END) as direct_count
                FROM users
                GROUP BY DATE(registered_at)
                ORDER BY reg_date ASC
            """, conn)
            
        if not df_time.empty:
            df_time["cumulative_total"] = df_time["daily_count"].cumsum()
            df_time["cumulative_viral"] = df_time["viral_count"].cumsum()
            df_time["cumulative_direct"] = df_time["direct_count"].cumsum()
            
            st.line_chart(df_time.set_index("reg_date")[["cumulative_total", "cumulative_direct", "cumulative_viral"]])
            st.caption("Blue: Total registrations | Orange: Direct (Campus Rep blasts) | Red: Compounding viral peer referrals")
        else:
            st.info("No timeline data found. Run seed_data.py to view charts.")
            
    with chart_col2:
        st.subheader("🎯 Acquisition Channel Breakdown")
        if kpis["channels"]:
            df_channels = pd.DataFrame(kpis["channels"])
            st.dataframe(df_channels.rename(columns={"channel": "Channel", "count": "Registrations"}), hide_index=True, use_container_width=True)
            
            st.subheader("🎓 Registrations by Engineering Branch")
            df_branches = pd.DataFrame(kpis["branches"])
            st.dataframe(df_branches.rename(columns={"branch": "Specialization", "count": "Students"}), hide_index=True, use_container_width=True)

    st.markdown("---")
    
    # College Leaderboard & Top Referrers
    lead_col1, lead_col2 = st.columns(2)
    
    with lead_col1:
        st.subheader("🏛 College vs College Leaderboard (The Pride Loop)")
        st.caption("College competition drives organic WhatsApp forwarding without extra spend.")
        colleges = get_college_leaderboard(8)
        if colleges:
            df_colleges = pd.DataFrame(colleges)
            st.bar_chart(df_colleges.set_index("college")["total_registrations"])
            
    with lead_col2:
        st.subheader("🔥 Top Student Advocates (Class Reps & Referrers)")
        st.caption("Micro-bounties (₹100 Amazon voucher for 25+ invites) trigger peer distribution.")
        top_refs = get_top_referrers(6)
        if top_refs:
            df_refs = pd.DataFrame(top_refs)
            st.dataframe(df_refs.rename(columns={
                "name": "Student Champion",
                "college": "College",
                "referral_code": "Ref Code",
                "referral_count": "Successful Invites",
                "unlocked_tier": "Reward Tier"
            }), hide_index=True, use_container_width=True)
            
    st.markdown("---")
    
    # Export student leads
    with st.expander("📥 Download Raw Registrations Dataset (Workshop Attendance List)"):
        with get_connection() as conn:
            all_users = pd.read_sql_query("SELECT user_id, name, college, branch, year, referral_code, referred_by, channel, registered_at FROM users", conn)
        st.write(f"Total Records: {len(all_users)}")
        csv_data = all_users.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Registrations CSV",
            data=csv_data,
            file_name="nxtwave_ai_workshop_registrations.csv",
            mime="text/csv"
        )

# -------------------------------------------------------------
# VIEW 2: INTERACTIVE BOT SIMULATOR
# -------------------------------------------------------------
elif nav_choice == "🤖 Interactive Bot Simulator":
    st.markdown('<div class="main-header">🤖 Telegram Bot Live Interactive Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Experience the frictionless 1-tap registration flow, referral generation, and reward unlocks as a student.</div>', unsafe_allow_html=True)
    
    sim_col1, sim_col2 = st.columns([1, 1])
    
    with sim_col1:
        st.subheader("📱 Student Registration Flow")
        sim_name = st.text_input("Student Name", value="Rahul Sharma")
        sim_college = st.selectbox("College Name", [
            "JNTU Hyderabad", "Anna University, Chennai", "VTU, Bangalore",
            "AKTU, Lucknow", "Pune University", "VIT Vellore", "Other College"
        ])
        sim_branch = st.selectbox("Engineering Branch", list(PROJECT_KNOWLEDGE_BASE.keys()))
        sim_ref = st.text_input("Referred by Code (Optional)", value="", help="Leave empty for direct registration, or enter e.g. RAHUL482")
        
        btn_register = st.button("🚀 Register with 1-Tap (Simulate Bot /start)", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚡ Bot Interactive Commands")
        col_cmd1, col_cmd2, col_cmd3 = st.columns(3)
        with col_cmd1:
            btn_leaderboard = st.button("🏆 /leaderboard", use_container_width=True)
        with col_cmd2:
            btn_ideas = st.button("💡 /ideas", use_container_width=True)
        with col_cmd3:
            btn_remind = st.button("⏰ Send Reminder", use_container_width=True)
            
    with sim_col2:
        st.subheader("💬 Bot Telegram Chat Output")
        
        if btn_register:
            sim_id = f"sim_{abs(hash(sim_name)) % 100000}"
            resp = process_bot_action("register", {
                "user_id": sim_id,
                "name": sim_name,
                "college": sim_college,
                "branch": sim_branch,
                "referred_by": sim_ref if sim_ref.strip() else None,
                "channel": "Interactive Simulator"
            })
            st.markdown(f'<div class="telegram-bubble">{resp["message"]}</div>', unsafe_allow_html=True)
            st.balloons()
            
        elif btn_leaderboard:
            resp = process_bot_action("leaderboard", {})
            st.markdown(f'<div class="telegram-bubble">{resp["message"]}</div>', unsafe_allow_html=True)
            
        elif btn_ideas:
            resp = process_bot_action("ideas", {"name": sim_name, "branch": sim_branch})
            st.markdown(f'<div class="telegram-bubble">{resp["message"]}</div>', unsafe_allow_html=True)
            
        elif btn_remind:
            resp = process_bot_action("reminder", {"name": sim_name, "hours_left": 24})
            st.markdown(f'<div class="telegram-bubble">{resp["message"]}</div>', unsafe_allow_html=True)
            
        else:
            # Default preview
            welcome = format_welcome_message(sim_name, sim_ref if sim_ref else None)
            st.markdown(f'<div class="telegram-bubble">{welcome}</div>', unsafe_allow_html=True)
            st.caption("👈 Fill in details on the left and tap 'Register with 1-Tap' to test.")

# -------------------------------------------------------------
# VIEW 3: AI PROJECT IDEATOR (/ideas)
# -------------------------------------------------------------
elif nav_choice == "💡 AI Project Ideator (/ideas)":
    st.markdown('<div class="main-header">🧠 AI Project Ideator & Resume Bullets Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Demonstrates how the bot hooks final-year engineering students by solving their #1 pain point: placement resume relevance.</div>', unsafe_allow_html=True)
    
    sel_branch = st.selectbox("Select Engineering Branch:", list(PROJECT_KNOWLEDGE_BASE.keys()))
    user_test_name = st.text_input("Student Name:", value="Sneha Patel")
    
    idea = generate_project_idea(sel_branch, user_test_name)
    proj = idea["project"]
    
    col_p1, col_p2 = st.columns([3, 2])
    
    with col_p1:
        st.subheader(f"🔥 Project: {proj['title']}")
        st.write(f"**Concept:** {proj['desc']}")
        st.markdown(f"**🛠 Tech Stack:** `{proj['tech_stack']}`")
        
        st.markdown("### 📄 Ready-to-Use Resume Bullet Points (ATS Optimized):")
        for b in proj["resume_bullets"]:
            st.markdown(f"- {b}")
            
        st.info(f"💼 **Why Recruiters Care:** {proj['recruiter_hook']}")
        
    with col_p2:
        st.subheader("📱 Telegram Output Preview")
        st.markdown(f'<div class="telegram-bubble">{idea["formatted_text"]}</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# VIEW 4: GROWTH PLAN & STRATEGIC LOGIC
# -------------------------------------------------------------
elif nav_choice == "📋 Growth Plan & Strategic Logic":
    st.markdown('<div class="main-header">📋 Growth Plan & Evaluation Answers</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete strategic breakdown answering the NxtWave Challenge prompts.</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🎯 7-Day Campaign Plan", "🧠 AI & Learning Notes", "⚖️ Judgment & Rejections"])
    
    with t1:
        st.markdown("""
        ### 1. Target Audience: Final-Year Engineering Students (2025 Batch)
        - **Core Persona:** Tier-2/3 college students facing placement freezes and intense interview competition.
        - **Emotional Trigger:** Fear of blank or generic resumes (CRUD apps, basic calculators).
        - **Irresistible Hook:** *"Build a deployed AI Agent + Get 3 Interview-Ready Resume Bullet Points in 60 Minutes."*
        
        ### 2. The 3 Prioritized Channels (Math to 500 Registrations)
        1. **Channel 1: Class Representatives (CR) Micro-Bounty Network (Primary Driver — 250 Registrations)**
           - Recruit 15-20 CRs across targeted colleges.
           - Allocate ₹1,200 (₹100 Amazon voucher for CRs driving 25+ verified registrations in their official batch WhatsApp group).
        2. **Channel 2: Peer-to-Peer Viral Referral Loop (150 Registrations)**
           - Built-in Telegram bot referral link + Reward Ladder (Unlock GitHub Starter Code at 2 invites; 50 Interview Qs at 5 invites).
           - K-factor of 0.35 turns 250 direct registrants into 350+ automatically.
        3. **Channel 3: Placement Telegram & Discord Drops (100 Registrations)**
           - High-value distribution: posting the free "AI Project Idea Generator" in tech placement communities.
           
        ### 3. Budget Deployment (₹2,000)
        - **₹1,200:** CR Performance Micro-Bounties (12 successful CRs × ₹100).
        - **₹500:** Top 3 Campus Referrer Grand Rewards (₹250, ₹150, ₹100).
        - **₹300:** Cloud hosting & domain buffer.
        - **Effective CPA:** **₹3.42 per student registration.**
        """)
        
    with t2:
        st.markdown("""
        ### AI + Learning Notes (Ask → Suggestion → Change)
        
        **Example 1: Paid Ads vs Campus Micro-Bounties**
        - *What I asked:* "How should I spend a ₹2,000 budget to get 500 student workshop registrations?"
        - *What AI suggested:* "Run Instagram story ads and Meta Lead Gen ads targeting engineering college students."
        - *What I changed:* **Rejected immediately.** Industry Meta CPL for Indian engineering students is ₹25–₹40. A ₹2,000 budget yields only 50–80 leads. Instead, pivoted 100% of the budget into Class Representative micro-bounties and viral referral rewards, unlocking 10x distribution via existing trusted WhatsApp channels.
        
        **Example 2: Traditional Landing Page vs 1-Tap Telegram Bot**
        - *What I asked:* "Design a high-converting registration landing page for this workshop."
        - *What AI suggested:* "Build a 10-section React/Tailwind landing page with curriculum, instructor bios, testimonials, and a multi-field Google Form."
        - *What I changed:* **Rejected.** On mobile networks, students drop off at 60%+ when faced with long forms and heavy pages. Furthermore, the brief noted: *'Everyone might build a landing page'*. Replaced it with a 1-tap Telegram bot that registers students without forms, tracks referral links natively, and automates 24h reminders.
        
        **Example 3: Generic AI Curriculum vs Placement Resume Bullets**
        - *What I asked:* "What value proposition should we offer during the 60-minute workshop?"
        - *What AI suggested:* "Teach fundamental AI concepts: neural networks, tokenization, and prompt engineering basics."
        - *What I changed:* **Replaced with practical placement currency.** Final-year students don't need theory in October; they need placement-clearing proof of work. Changed the core deliverable to: *"Build an AI Agent + Get 3 ATS-optimized resume bullet points."*
        """)
        
    with t3:
        st.markdown("""
        ### Judgment & Evaluation Answers
        
        **1. What changed between your first idea and final solution?**
        - *First Idea:* A standard Google Form + WhatsApp Community link promoted through college Instagram pages.
        - *Final Solution:* A Telegram bot growth engine with unique referral codes, an automated reward ladder, branch-specific AI project idea generator, and an executive Streamlit analytics dashboard tracking K-Factor and college leaderboards.
        
        **2. If you had another 24 hours, what would you improve?**
        - Integrate the official WhatsApp Cloud API so the identical 1-tap flow runs directly inside WhatsApp.
        - Add an automated GitHub integration where students can submit their repository post-workshop and receive an auto-graded NxtWave Verified AI Builder LinkedIn badge.
        
        **3. What did AI suggest that you deliberately rejected and why?**
        - AI suggested offering a "Free Certificate of Participation" as the primary marketing hook. I deliberately rejected this because Indian engineering students already possess dozens of participation certificates that recruiters discount. Instead, I shifted the hook to **tangible placement outcomes: ready-to-paste resume bullet points and a deployed GitHub repository.**
        """)
