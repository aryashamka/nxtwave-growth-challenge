"""
Automated Test Suite for NxtWave Growth Engine
Verifies core growth loops, database persistence, referral cascades,
and KPI calculations.
"""

import os
import unittest
import sys
import gc

# Ensure module path is included
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db, register_user, get_user, get_referral_count,
    get_top_referrers, get_college_leaderboard, get_growth_kpis
)
from ai_recommender import generate_project_idea
from bot import process_bot_action, format_welcome_message, format_registration_pass

TEST_DB = "test_growth.db"

class TestGrowthEngine(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        gc.collect()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except Exception:
                pass
        init_db(TEST_DB)
        
    @classmethod
    def tearDownClass(cls):
        gc.collect()
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except Exception:
                pass
            
    def test_1_direct_registration(self):
        is_new, msg, user = register_user(
            user_id="U1",
            name="Rahul Sharma",
            username="rahuls",
            college="JNTU Hyderabad",
            branch="Computer Science & Engineering (CSE)",
            year="Final Year (2025)",
            db_path=TEST_DB
        )
        self.assertTrue(is_new)
        self.assertIn("RAHUL", user["referral_code"])
        self.assertIsNone(user["referred_by"])
        
    def test_2_referral_chain_and_k_factor(self):
        # 1. Register seed champion (CR)
        _, _, cr = register_user(
            user_id="CR_1",
            name="Priya Patel",
            username="priyap",
            college="Anna University, Chennai",
            branch="Computer Science & Engineering (CSE)",
            year="Final Year (2025)",
            db_path=TEST_DB
        )
        cr_ref = cr["referral_code"]
        
        # 2. Register 3 friends using CR's referral code
        for i in range(3):
            register_user(
                user_id=f"STUDENT_{i}",
                name=f"Student {i}",
                username=f"student_{i}",
                college="Anna University, Chennai",
                branch="Information Technology (IT)",
                year="Final Year (2025)",
                referred_by=cr_ref,
                db_path=TEST_DB
            )
            
        ref_count = get_referral_count(cr_ref, TEST_DB)
        self.assertEqual(ref_count, 3)
        
        # Check reward tier: >= 2 referrals unlocks Tier 1
        updated_cr = get_user("CR_1", TEST_DB)
        self.assertEqual(updated_cr["unlocked_tier"], 1)
        
        # Check Growth KPIs
        kpis = get_growth_kpis(TEST_DB)
        self.assertEqual(kpis["total_registrations"], 5)  # U1 + CR_1 + 3 students
        self.assertEqual(kpis["viral_registrations"], 3)
        self.assertEqual(kpis["direct_registrations"], 2)
        self.assertEqual(kpis["k_factor"], 1.5)  # 3 viral / 2 direct = 1.5
        
    def test_3_ai_project_ideator(self):
        branches = [
            "Computer Science & Engineering (CSE)",
            "Information Technology (IT)",
            "Artificial Intelligence & Data Science",
            "Electronics & Communication (ECE)",
            "Mechanical & Allied (Pivot to Tech)"
        ]
        for b in branches:
            res = generate_project_idea(b, "Test Student")
            self.assertIn("project", res)
            self.assertTrue(len(res["project"]["resume_bullets"]) >= 3)
            self.assertIn("Tech Stack", res["formatted_text"])
            
    def test_4_bot_action_dispatcher(self):
        resp = process_bot_action("leaderboard", {})
        self.assertEqual(resp["status"], "ok")
        self.assertIn("LEADERBOARD", resp["message"])

if __name__ == "__main__":
    unittest.main()
