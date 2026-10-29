# NxtWave Growth Challenge — 500 Registrations Sprint Engine
### Submission for Round 1: NxtWave Growth Intern Challenge
**Project:** Telegram Conversational Growth Bot & Live Analytics Command Center  
**Campaign:** *"Build Your First AI Project in 60 Minutes"*  
**Author:** Candidate Submission  

---

## 🚀 Quickstart: Run the Prototype in 60 Seconds

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Install Dependencies
```bash
cd nxtwave-growth-challenge
pip install -r requirements.txt
```

### 3. Seed Realistic Simulation Data
Populates 438+ realistic student registrations, multi-tier referral chains, and college standings:
```bash
python seed_data.py
```

### 4. Launch the Executive Dashboard & Live Bot Simulator
* **Option A: Streamlit UI:**
  ```bash
  streamlit run dashboard.py
  ```
  Open `http://localhost:8501`.
* **Option B: Vercel Web Serverless App (Local):**
  ```bash
  python api/index.py
  ```
  Open `http://localhost:5000`.

### 5. Run Automated Tests
```bash
python test_bot.py
```

---

## 🌐 Deploying Live to Vercel (1-Click)

This repository is already configured with `vercel.json` and `api/index.py`:
1. Push this folder to a GitHub repository:
   ```bash
   git init && git add . && git commit -m "Initial commit"
   git remote add origin https://github.com/<YOUR_USER>/nxtwave-growth-challenge.git
   git push -u origin main
   ```
2. Go to [vercel.com](https://vercel.com) → **Add New Project** → Select your repo.
3. Click **Deploy**. Your app will be live at `https://nxtwave-growth-challenge.vercel.app`!
*(See `VERCEL_DEPLOYMENT_GUIDE.md` for full step-by-step instructions).*

---

## 📁 Repository & Submission Structure

```
nxtwave-growth-challenge/
│
├── database.py              # SQLite storage layer: registrations, referrals, K-factor, leaderboard
├── seed_data.py             # Realistic 7-day data seeder (438+ students across 12 colleges)
├── ai_recommender.py        # /ideas AI Project Ideator: customized blueprints + resume bullets
├── bot.py                   # Telegram Bot engine (state machine, referral tracker, reminder alerts)
├── dashboard.py             # Streamlit Executive Growth Dashboard & Live Bot Simulator
├── test_bot.py              # Automated test suite (100% passing)
├── requirements.txt         # Core dependencies (streamlit, pandas, requests)
│
└── deliverables/            # COMPLETE SUBMISSION DELIVERABLES
    ├── 1_GROWTH_PLAN_DECK.md        # Max 5 Slides / 2 Pages Growth Plan (Ready for presentation)
    ├── 2_AI_AND_LEARNING_NOTES.md  # 3 Concrete Ask → AI Suggestion → Deliberate Rejection cases
    ├── 3_VIDEO_WALKTHROUGH_SCRIPT.md # Word-for-word 3-Minute Video Walkthrough Script with timestamps
    └── 4_REFLECTIONS_AND_JUDGMENT.md# In-depth answers to the 3 mandatory evaluation questions
```

---

## 🎯 Key Strategic Highlights

1. **Why No Paid Ads?**  
   At an industry benchmark CPL of ₹25–₹40, spending the ₹2,000 budget on Meta/Instagram ads would exhaust the budget on only 50–80 leads. Instead, ₹1,200 is deployed as ₹100 micro-bounties for 12 Class Representatives (CRs), driving 275+ direct registrations via trusted WhatsApp groups.
2. **The Compounding Viral Loop (K-Factor = 0.35):**  
   Every registered student receives an Admit Pass with a personalized referral code (`t.me/Bot?start=REF_CODE`) and an automated **Reward Ladder** (unlocking ATS Resume Bullets at 2 invites; GitHub Starter Code at 5 invites; VIP Review at 10 invites).
3. **The Pride Loop (`/leaderboard`):**  
   Colleges compete against each other in real-time. Students actively share links in their batch groups to push their college up the standings.
4. **Placement Currency over Certificates (`/ideas`):**  
   Rather than advertising another generic "participation certificate", the campaign offers **immediate placement value**: 3 ATS-optimized resume bullet points tailored to the student's specific engineering branch.
5. **Effective Acquisition Cost:**  
   **₹3.42 per student registration** (90% cheaper than paid ads).

---

## 🤖 Running on Live Telegram (Optional)
To link this directly to an active Telegram Bot:
1. Open Telegram and create a bot using `@BotFather` to get a `TELEGRAM_BOT_TOKEN`.
2. Set the token:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"   # Mac/Linux
   set TELEGRAM_BOT_TOKEN="your_bot_token_here"      # Windows CMD
   $env:TELEGRAM_BOT_TOKEN="your_bot_token_here"     # Windows PowerShell
   ```
3. Run the live polling daemon:
   ```bash
   python bot.py
   ```
