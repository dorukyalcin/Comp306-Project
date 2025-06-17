#!/usr/bin/env python3
"""
Debug Query 5: Betting Behavior Cohort Analysis
==============================================

This script tests Query 5 directly to debug why it might be returning empty results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def debug_query5():
    """Debug Query 5 step by step"""
    
    print("🔍 Debugging Query 5: Betting Behavior Cohort Analysis")
    print("=" * 60)
    
    with app.app_context():
        # First, let's check if we have the basic data
        print("\n📊 Checking basic data...")
        
        # Check users
        users_count = db.session.execute(text("SELECT COUNT(*) FROM users WHERE is_admin = FALSE")).scalar()
        print(f"Non-admin users: {users_count}")
        
        # Check bets
        bets_count = db.session.execute(text("SELECT COUNT(*) FROM bets")).scalar()
        print(f"Total bets: {bets_count}")
        
        # Check cohort users specifically
        cohort_users = db.session.execute(text("SELECT COUNT(*) FROM users WHERE username LIKE 'cohort_user_%'")).scalar()
        print(f"Cohort users: {cohort_users}")
        
        # Check bets by cohort users
        cohort_bets = db.session.execute(text("""
            SELECT COUNT(*) FROM bets b 
            JOIN users u ON b.user_id = u.user_id 
            WHERE u.username LIKE 'cohort_user_%'
        """)).scalar()
        print(f"Bets by cohort users: {cohort_bets}")
        
        print("\n🧩 Testing Query 5 components...")
        
        # Test user_cohorts CTE
        print("\n1. Testing user_cohorts CTE...")
        user_cohorts_sql = """
        SELECT 
            user_id,
            username,
            DATE_TRUNC('month', created_at) as cohort_month,
            created_at
        FROM users 
        WHERE is_admin = FALSE
        ORDER BY user_id
        LIMIT 5
        """
        result = db.session.execute(text(user_cohorts_sql))
        rows = result.fetchall()
        print(f"User cohorts sample: {len(rows)} rows")
        for row in rows[:3]:
            print(f"  {row.username}, {row.cohort_month}")
        
        # Test user_first_bet CTE
        print("\n2. Testing user_first_bet CTE...")
        first_bet_sql = """
        SELECT 
            b.user_id,
            MIN(DATE(b.placed_at)) as first_bet_date,
            DATE_TRUNC('month', MIN(b.placed_at)) as first_bet_month
        FROM bets b
        GROUP BY b.user_id
        ORDER BY b.user_id
        LIMIT 5
        """
        result = db.session.execute(text(first_bet_sql))
        rows = result.fetchall()
        print(f"First bet data sample: {len(rows)} rows")
        for row in rows[:3]:
            print(f"  User {row.user_id}: {row.first_bet_date}")
        
        # Test the full query but simplified
        print("\n3. Testing simplified full query...")
        simplified_sql = """
        WITH user_cohorts AS (
            SELECT 
                user_id,
                username,
                DATE_TRUNC('month', created_at) as cohort_month,
                created_at
            FROM users 
            WHERE is_admin = FALSE
        ),
        user_first_bet AS (
            SELECT 
                b.user_id,
                MIN(DATE(b.placed_at)) as first_bet_date
            FROM bets b
            GROUP BY b.user_id
        ),
        user_betting_journey AS (
            SELECT 
                uc.user_id,
                uc.username,
                uc.cohort_month,
                ufb.first_bet_date,
                COUNT(b.bet_id) as total_bets
            FROM user_cohorts uc
            LEFT JOIN user_first_bet ufb ON uc.user_id = ufb.user_id
            LEFT JOIN bets b ON uc.user_id = b.user_id
            GROUP BY uc.user_id, uc.username, uc.cohort_month, ufb.first_bet_date
            HAVING COUNT(b.bet_id) > 0
        )
        SELECT 
            username,
            cohort_month,
            total_bets
        FROM user_betting_journey
        ORDER BY total_bets DESC
        LIMIT 10
        """
        
        result = db.session.execute(text(simplified_sql))
        rows = result.fetchall()
        print(f"Simplified query results: {len(rows)} rows")
        for row in rows[:5]:
            print(f"  {row.username}: {row.total_bets} bets, cohort {row.cohort_month}")
        
        # Test the actual Query 5 from app.py
        print("\n4. Testing actual Query 5...")
        full_query = """
        WITH user_cohorts AS (
            SELECT 
                user_id,
                username,
                DATE_TRUNC('month', created_at) as cohort_month,
                created_at
            FROM users 
            WHERE is_admin = FALSE
        ),
        user_first_bet AS (
            SELECT 
                b.user_id,
                MIN(DATE(b.placed_at)) as first_bet_date,
                DATE_TRUNC('month', MIN(b.placed_at)) as first_bet_month
            FROM bets b
            GROUP BY b.user_id
        ),
        user_betting_journey AS (
            SELECT 
                uc.user_id,
                uc.username,
                uc.cohort_month,
                ufb.first_bet_date,
                ufb.first_bet_month,
                (ufb.first_bet_date - uc.created_at::DATE) as days_to_first_bet,
                COUNT(b.bet_id) as total_bets,
                COUNT(DISTINCT DATE(b.placed_at)) as betting_days,
                COUNT(DISTINCT r.game_id) as games_tried,
                SUM(b.amount) as total_wagered,
                AVG(b.amount) as avg_bet_size,
                STDDEV(b.amount) as bet_size_variance,
                MIN(b.placed_at) as betting_start,
                MAX(b.placed_at) as last_bet_date,
                (DATE(MAX(b.placed_at)) - DATE(MIN(b.placed_at))) + 1 as betting_lifespan_days
            FROM user_cohorts uc
            LEFT JOIN user_first_bet ufb ON uc.user_id = ufb.user_id
            LEFT JOIN bets b ON uc.user_id = b.user_id
            LEFT JOIN rounds r ON b.round_id = r.round_id
            GROUP BY uc.user_id, uc.username, uc.cohort_month, uc.created_at, ufb.first_bet_date, ufb.first_bet_month
            HAVING COUNT(b.bet_id) > 0
        ),
        user_behavior_segments AS (
            SELECT 
                ubj.*,
                CASE 
                    WHEN total_bets >= 50 AND betting_lifespan_days >= 60 THEN 'High Value Regular'
                    WHEN total_bets >= 20 AND betting_lifespan_days >= 30 THEN 'Active Player'
                    WHEN total_bets >= 10 THEN 'Casual Player'
                    WHEN total_bets >= 5 THEN 'Trial User'
                    ELSE 'One-time Player'
                END as player_segment,
                CASE 
                    WHEN avg_bet_size >= 100 THEN 'High Roller'
                    WHEN avg_bet_size >= 50 THEN 'Medium Stake'
                    WHEN avg_bet_size >= 20 THEN 'Regular Stake'
                    ELSE 'Low Stake'
                END as stake_category,
                CASE 
                    WHEN betting_days > 0 
                    THEN ROUND(total_bets::NUMERIC / betting_days, 2)
                    ELSE 0 
                END as bets_per_active_day
            FROM user_betting_journey
        )
        SELECT 
            username,
            cohort_month,
            days_to_first_bet,
            total_bets,
            betting_days,
            games_tried,
            ROUND(total_wagered, 2) as total_wagered,
            ROUND(avg_bet_size, 2) as avg_bet_size,
            betting_lifespan_days,
            bets_per_active_day,
            player_segment,
            stake_category,
            RANK() OVER (ORDER BY total_wagered DESC) as value_rank
        FROM user_behavior_segments
        ORDER BY total_wagered DESC
        LIMIT 15;
        """
        
        try:
            result = db.session.execute(text(full_query))
            rows = result.fetchall()
            print(f"✅ Full Query 5 executed successfully!")
            print(f"📊 Results: {len(rows)} rows")
            
            if rows:
                print("\n🎯 Sample results:")
                for row in rows[:3]:
                    print(f"  {row.username}: {row.total_bets} bets, ${row.total_wagered}, {row.player_segment}")
            else:
                print("❌ No results returned from Query 5")
                
        except Exception as e:
            print(f"❌ Error in full Query 5: {str(e)}")

def main():
    debug_query5()

if __name__ == "__main__":
    main() 