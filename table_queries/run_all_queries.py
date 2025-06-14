#!/usr/bin/env python3
"""
Master script to run all table queries
This script executes SELECT * FROM queries for all tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from horses import query_horses
from horse_runners import query_horse_runners
from horse_results import query_horse_results
from rounds import query_rounds
from outcomes import query_outcomes
from bets import query_bets
from games_table import query_games

def run_all_table_queries():
    """Run SELECT * queries for all database tables"""
    
    print("🔍 RUNNING ALL TABLE QUERIES")
    print("=" * 80)
    print("Executing SELECT * FROM queries for all tables...\n")
    
    try:
        # Run each table query
        query_games()
        print("\n" + "="*80 + "\n")
        
        query_rounds()
        print("\n" + "="*80 + "\n")
        
        query_horses()
        print("\n" + "="*80 + "\n")
        
        query_horse_runners()
        print("\n" + "="*80 + "\n")
        
        query_horse_results()
        print("\n" + "="*80 + "\n")
        
        query_outcomes()
        print("\n" + "="*80 + "\n")
        
        query_bets()
        print("\n" + "="*80 + "\n")
        
        print("✅ All table queries completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running table queries: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_table_queries() 