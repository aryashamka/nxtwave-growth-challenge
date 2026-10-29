# Deployment Guide: Vercel & Streamlit Cloud
## NxtWave Growth Challenge — Live Prototype Deployment

You have **two distinct ways** to deploy this prototype live so you can submit a working link in your application form.

---

## ⚡ Option 1: Deploy to Vercel (Fastest & Permanent `.vercel.app` Link)

We have already configured:
- `vercel.json` (serverless routing)
- `api/index.py` (Flask serverless backend with auto-seeding SQLite in `/tmp`)
- `public/index.html` (interactive dashboard, charts, bot simulator, and growth slides)

### Method A: Deploy via GitHub + Vercel Dashboard (No CLI needed)
1. Initialize git and push this project to your GitHub account:
   ```bash
   cd C:\Users\aryas\.gemini\antigravity\scratch\nxtwave-growth-challenge
   git init
   git add .
   git commit -m "NxtWave Growth Challenge submission"
   # Create a new repository on github.com (e.g. nxtwave-growth-challenge)
   git remote add origin https://github.com/<YOUR_USERNAME>/nxtwave-growth-challenge.git
   git branch -M main
   git push -u origin main
   ```
2. Go to [vercel.com](https://vercel.com) and log in (with GitHub).
3. Click **"Add New..."** → **"Project"**.
4. Import your `nxtwave-growth-challenge` repository.
5. Leave the framework preset as **"Other"** (or Root).
6. Click **Deploy**.
7. In ~45 seconds, your live link will be ready: `https://nxtwave-growth-challenge.vercel.app`!

### Method B: Deploy via Vercel CLI (Command Line)
If you have Node.js and Vercel CLI installed:
```bash
cd C:\Users\aryas\.gemini\antigravity\scratch\nxtwave-growth-challenge
vercel
```
Follow the 3 quick prompts (login, link project, deploy). Done!

---

## 🎈 Option 2: Deploy to Streamlit Community Cloud (Native Python Streamlit)

If you prefer the native Streamlit UI (`dashboard.py`):

1. Push this project to GitHub (same as Step 1 above).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**.
4. Select your repository: `<YOUR_USERNAME>/nxtwave-growth-challenge`.
5. Set **Main file path** to: `dashboard.py`.
6. Click **Deploy!**
7. You will receive a live URL: `https://<YOUR_APP>.streamlit.app`.

---

## 🔍 Why this Architecture Was Chosen

* **The Challenge:** Streamlit apps require a persistent long-running WebSocket server. Vercel is a serverless platform designed for ephemeral HTTP functions.
* **Our Solution:** We created a dual-interface architecture:
  1. For **Streamlit Cloud**, `dashboard.py` runs natively with Python Streamlit.
  2. For **Vercel**, `api/index.py` runs as a high-speed Python serverless function and serves `public/index.html` with Tailwind CSS, Chart.js, and the interactive Bot Simulator.
  3. Both share the exact same growth database logic (`database.py`) and AI ideator (`ai_recommender.py`).
