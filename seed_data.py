"""
Seed script to populate realistic simulation data for the 7-day campaign.
Demonstrates:
- 435 total registrations across 12 prominent engineering colleges
- 3-tier referral chains showing active K-factor (0.35)
- Seeded Class Representatives (CRs) at the top of the leaderboard
"""

import datetime
import random
import os
from database import init_db, register_user, get_connection, DB_PATH

COLLEGES = [
    "JNTU Hyderabad",
    "Anna University, Chennai",
    "VTU (BMSCE/PES), Bangalore",
    "AKTU, Lucknow",
    "Pune University (COEP/MIT)",
    "SRM University",
    "Osmania University, Hyderabad",
    "Vellore Institute of Technology (VIT)",
    "Andhra University, Vizag",
    "Thapar University, Patiala",
    "KIIT, Bhubaneswar",
    "GGSIPU, Delhi"
]

BRANCHES = [
    ("Computer Science & Engineering (CSE)", 0.45),
    ("Information Technology (IT)", 0.20),
    ("Artificial Intelligence & Data Science", 0.18),
    ("Electronics & Communication (ECE)", 0.12),
    ("Mechanical & Allied (Pivot to Tech)", 0.05)
]

FIRST_NAMES = [
    "Rahul", "Priya", "Ankit", "Sneha", "Karthik", "Rohan", "Ananya", "Vikram",
    "Swati", "Aditya", "Divya", "Siddharth", "Pooja", "Arjun", "Megha", "Nikhil",
    "Sai", "Tanvi", "Varun", "Harsh", "Ritika", "Gaurav", "Shreya", "Abhishek",
    "Kavya", "Manish", "Deepika", "Pranav", "Nisha", "Akhil", "Tejas", "Sanjana"
]

LAST_NAMES = [
    "Sharma", "Verma", "Reddy", "Patel", "Rao", "Nair", "Iyer", "Kumar",
    "Singh", "Gupta", "Joshi", "Choudhury", "Mishra", "Banerjee", "Das", "Menon"
]

CHANNELS = [
    ("WhatsApp College CR Blast", 0.52),
    ("Peer Referral Invite", 0.33),
    ("Placement Telegram Group", 0.10),
    ("LinkedIn/Direct", 0.05)
]

def choose_weighted(items):
    choices, weights = zip(*items)
    return random.choices(choices, weights=weights, k=1)[0]

def populate_simulation_data(target_count: int = 438, db_path: str = DB_PATH):
    # Remove existing DB if fresh run
    if os.path.exists(db_path):
        os.remove(db_path)
    
    init_db(db_path)
    print(f"[*] Initialized fresh database at {db_path}")
    
    # Step 1: Create 15 Class Representatives (Seed Champions)
    cr_pool = []
    print("[*] Seeding 15 College Class Representatives (Campus Champions)...")
    for i in range(15):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        college = COLLEGES[i % len(COLLEGES)]
        branch = choose_weighted(BRANCHES)
        user_id = f"CR_100{i+1}"
        username = f"cr_{name.lower().replace(' ', '_')}"
        
        _, _, user = register_user(
            user_id=user_id,
            name=name,
            username=username,
            college=college,
            branch=branch,
            year="Final Year (2025)",
            referred_by=None,
            channel="Campus Ambassador Outreach",
            db_path=db_path
        )
        cr_pool.append(user["referral_code"])
    
    # Step 2: Seed organic direct and viral registrations over 7 simulated days
    now = datetime.datetime.now()
    generated_referral_codes = list(cr_pool)
    
    print(f"[*] Generating {target_count - 15} student registrations across 7-day timeline...")
    for i in range(16, target_count + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        college = random.choice(COLLEGES)
        branch = choose_weighted(BRANCHES)
        user_id = f"TG_{10000 + i}"
        username = f"{name.lower().replace(' ', '')}{random.randint(10, 99)}"
        channel = choose_weighted(CHANNELS)
        
        # Determine if referred (viral loop)
        referred_by = None
        if channel == "Peer Referral Invite" and generated_referral_codes:
            # 60% chance to be referred by top CRs, 40% by normal peers
            if random.random() < 0.65:
                referred_by = random.choice(cr_pool)
            else:
                referred_by = random.choice(generated_referral_codes)
        elif channel == "WhatsApp College CR Blast":
            referred_by = random.choice(cr_pool)
            
        is_new, _, user = register_user(
            user_id=user_id,
            name=name,
            username=username,
            college=college,
            branch=branch,
            year="Final Year (2025)",
            referred_by=referred_by,
            channel=channel,
            db_path=db_path
        )
        
        if is_new and random.random() < 0.4:
            generated_referral_codes.append(user["referral_code"])
    
    # Backdate registrations to simulate a realistic 7-day growth S-curve
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row["user_id"] for row in cursor.fetchall()]
        
        # Day distribution (gradual ramp up -> massive viral surge on Day 4 & 5)
        day_weights = [0.08, 0.12, 0.18, 0.24, 0.22, 0.11, 0.05]
        
        for uid in user_ids:
            day_offset = random.choices(range(7), weights=day_weights, k=1)[0]
            hour_offset = random.randint(9, 23)
            min_offset = random.randint(0, 59)
            reg_time = now - datetime.timedelta(days=(6 - day_offset), hours=(23 - hour_offset), minutes=min_offset)
            cursor.execute("UPDATE users SET registered_at = ? WHERE user_id = ?", (reg_time.strftime("%Y-%m-%d %H:%M:%S"), uid))
        conn.commit()
    
    print(f"[+] Successfully seeded simulation dataset with {target_count} registrations!")

if __name__ == "__main__":
    populate_simulation_data()
