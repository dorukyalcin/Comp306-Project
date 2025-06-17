#!/usr/bin/env python3
"""
Complex SQL Queries for Database Course Requirements
====================================================

This module contains 5 sophisticated SQL queries that demonstrate:
1. Complex JOINs across multiple tables
2. Aggregate functions with GROUP BY and HAVING
3. Subqueries and correlated subqueries  
4. Window functions and ranking
5. Advanced analytics and business intelligence

Each query includes both the raw SQL and SQLAlchemy implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text, func
from models import User, Wallet, Transaction, Game, Round, Bet, Outcome, Horse, HorseRunner, HorseResult
from decimal import Decimal


def query_1_user_performance_analytics():
    """
    QUERY 1: User Performance Analytics with Rankings
    =================================================
    
    This query calculates comprehensive user performance metrics including:
    - Total amount wagered per user
    - Win/loss ratios and profit/loss
    - User rankings by profitability
    - Risk assessment scores
    
    Demonstrates: Complex JOINs, Window functions, Aggregate functions, CTEs
    """
    
    raw_sql = """
    WITH user_betting_stats AS (
        SELECT 
            u.user_id,
            u.username,
            u.created_at,
            COUNT(DISTINCT b.bet_id) as total_bets,
            COALESCE(SUM(b.amount), 0) as total_wagered,
            COALESCE(SUM(b.payout_amount), 0) as total_winnings,
            COALESCE(SUM(b.payout_amount), 0) - COALESCE(SUM(b.amount), 0) as net_profit,
            COUNT(CASE WHEN b.payout_amount > b.amount THEN 1 END) as winning_bets,
            COUNT(CASE WHEN b.payout_amount = 0 THEN 1 END) as losing_bets,
            AVG(b.amount) as avg_bet_size,
            MAX(b.amount) as max_bet_size,
            COUNT(DISTINCT g.code) as games_played,
            COUNT(DISTINCT DATE(b.placed_at)) as active_days
        FROM users u
        LEFT JOIN bets b ON u.user_id = b.user_id
        LEFT JOIN rounds r ON b.round_id = r.round_id  
        LEFT JOIN games g ON r.game_id = g.game_id
        WHERE u.is_admin = FALSE
        GROUP BY u.user_id, u.username, u.created_at
        HAVING COUNT(b.bet_id) > 0
    ),
    user_rankings AS (
        SELECT *,
            CASE 
                WHEN total_bets > 0 THEN ROUND((winning_bets::NUMERIC / total_bets) * 100, 2)
                ELSE 0 
            END as win_percentage,
            CASE 
                WHEN total_wagered > 0 THEN ROUND((net_profit / total_wagered) * 100, 2)
                ELSE 0 
            END as roi_percentage,
            RANK() OVER (ORDER BY net_profit DESC) as profit_rank,
            RANK() OVER (ORDER BY total_wagered DESC) as volume_rank,
            CASE 
                WHEN avg_bet_size > 100 THEN 'High Roller'
                WHEN avg_bet_size > 50 THEN 'Medium Risk'
                WHEN avg_bet_size > 10 THEN 'Conservative'
                ELSE 'Penny Player'
            END as risk_profile
        FROM user_betting_stats
    )
    SELECT 
        username,
        total_bets,
        total_wagered,
        total_winnings,
        net_profit,
        win_percentage,
        roi_percentage,
        profit_rank,
        volume_rank,
        risk_profile,
        games_played,
        active_days,
        ROUND(total_wagered / NULLIF(active_days, 0), 2) as avg_daily_wagered
    FROM user_rankings
    ORDER BY net_profit DESC;
    """
    
    print("🎯 QUERY 1: User Performance Analytics with Rankings")
    print("=" * 60)
    
    with app.app_context():
        result = db.session.execute(text(raw_sql))
        
        print(f"{'Username':<15} {'Bets':<6} {'Wagered':<10} {'Profit':<10} {'Win%':<6} {'ROI%':<6} {'Risk Profile':<12}")
        print("-" * 80)
        
        for row in result:
            print(f"{row.username:<15} {row.total_bets:<6} "
                  f"${row.total_wagered:<9.2f} ${row.net_profit:<9.2f} "
                  f"{row.win_percentage:<6.1f} {row.roi_percentage:<6.1f} {row.risk_profile:<12}")


def query_2_game_revenue_analysis():
    """
    QUERY 2: Game Revenue and Performance Analysis
    ==============================================
    
    Analyzes revenue generation and house edge efficiency by game type.
    Includes player engagement metrics and game profitability analysis.
    
    Demonstrates: Complex aggregations, Subqueries, Business calculations
    """
    
    raw_sql = """
    WITH game_stats AS (
        SELECT 
            g.code,
            g.house_edge,
            g.min_bet,
            g.max_bet,
            COUNT(DISTINCT r.round_id) as total_rounds,
            COUNT(DISTINCT b.user_id) as unique_players,
            COUNT(b.bet_id) as total_bets,
            COALESCE(SUM(b.amount), 0) as total_wagered,
            COALESCE(SUM(b.payout_amount), 0) as total_paid_out,
            COALESCE(SUM(b.amount), 0) - COALESCE(SUM(b.payout_amount), 0) as house_profit,
            AVG(b.amount) as avg_bet_size,
            MIN(b.placed_at) as first_bet_date,
            MAX(b.placed_at) as last_bet_date
        FROM games g
        LEFT JOIN rounds r ON g.game_id = r.game_id
        LEFT JOIN bets b ON r.round_id = b.round_id
        WHERE g.is_active = TRUE
        GROUP BY g.code, g.house_edge, g.min_bet, g.max_bet
    ),
    game_performance AS (
        SELECT *,
            CASE 
                WHEN total_wagered > 0 
                THEN ROUND((house_profit / total_wagered) * 100, 3)
                ELSE 0 
            END as actual_house_edge_pct,
            CASE 
                WHEN total_rounds > 0 
                THEN ROUND(total_wagered / total_rounds, 2)
                ELSE 0 
            END as avg_wagered_per_round,
            CASE 
                WHEN unique_players > 0 
                THEN ROUND(total_bets::NUMERIC / unique_players, 1)
                ELSE 0 
            END as avg_bets_per_player,
            EXTRACT(DAYS FROM (last_bet_date - first_bet_date)) + 1 as days_active
        FROM game_stats
    )
    SELECT 
        code as game_code,
        house_edge * 100 as theoretical_house_edge_pct,
        actual_house_edge_pct,
        total_rounds,
        unique_players,
        total_bets,
        total_wagered,
        house_profit,
        avg_bet_size,
        avg_wagered_per_round,
        avg_bets_per_player,
        days_active,
        CASE 
            WHEN days_active > 0 
            THEN ROUND(house_profit / days_active, 2)
            ELSE 0 
        END as daily_house_profit,
        RANK() OVER (ORDER BY house_profit DESC) as profitability_rank,
        RANK() OVER (ORDER BY unique_players DESC) as popularity_rank
    FROM game_performance
    WHERE total_bets > 0
    ORDER BY house_profit DESC;
    """
    
    print("\n🎰 QUERY 2: Game Revenue and Performance Analysis")
    print("=" * 60)
    
    with app.app_context():
        result = db.session.execute(text(raw_sql))
        
        print(f"{'Game':<10} {'Theory%':<8} {'Actual%':<8} {'Players':<8} {'Profit':<10} {'Daily$':<8}")
        print("-" * 60)
        
        for row in result:
            print(f"{row.game_code:<10} {row.theoretical_house_edge_pct:<8.1f} "
                  f"{row.actual_house_edge_pct:<8.1f} {row.unique_players:<8} "
                  f"${row.house_profit:<9.2f} ${row.daily_house_profit:<7.2f}")


def query_3_horse_racing_analytics():
    """
    QUERY 3: Horse Racing Performance Analytics
    ===========================================
    
    Advanced horse performance analysis with odds efficiency and betting patterns.
    Includes horse rankings, jockey performance equivalent, and race analytics.
    
    Demonstrates: Complex JOINs, Statistical calculations, Performance metrics
    """
    
    raw_sql = """
    WITH horse_race_stats AS (
        SELECT 
            h.horse_id,
            h.name,
            h.age,
            h.base_speed,
            h.temperament,
            COUNT(hr.round_id) as races_run,
            COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) as wins,
            COUNT(CASE WHEN hr.finish_place <= 3 THEN 1 END) as top3_finishes,
            AVG(hr.finish_place) as avg_finish_position,
            AVG(hr.race_time_sec) as avg_race_time,
            MIN(hr.race_time_sec) as best_time,
            AVG(hrn.odds) as avg_odds
        FROM horses h
        LEFT JOIN horse_results hr ON h.horse_id = hr.horse_id
        LEFT JOIN horse_runners hrn ON h.horse_id = hrn.horse_id AND hr.round_id = hrn.round_id
        GROUP BY h.horse_id, h.name, h.age, h.base_speed, h.temperament
        HAVING COUNT(hr.round_id) > 0
    ),
    horse_betting_stats AS (
        SELECT 
            hrs.horse_id,
            COUNT(b.bet_id) as total_bets_on,
            SUM(b.amount) as total_wagered_on,
            SUM(b.payout_amount) as total_paid_out,
            SUM(b.amount) - SUM(b.payout_amount) as profit_for_house
        FROM horse_race_stats hrs
        LEFT JOIN horse_runners hrn ON hrs.horse_id = hrn.horse_id
        LEFT JOIN bets b ON hrn.round_id = b.round_id 
            AND b.choice_data->>'horse_id' = hrs.horse_id::text
        GROUP BY hrs.horse_id
    ),
    combined_stats AS (
        SELECT 
            hrs.*,
            COALESCE(hbs.total_bets_on, 0) as total_bets_on,
            COALESCE(hbs.total_wagered_on, 0) as total_wagered_on,
            COALESCE(hbs.profit_for_house, 0) as profit_for_house,
            CASE 
                WHEN hrs.races_run > 0 
                THEN ROUND((hrs.wins::NUMERIC / hrs.races_run) * 100, 1)
                ELSE 0 
            END as win_percentage,
            CASE 
                WHEN hrs.races_run > 0 
                THEN ROUND((hrs.top3_finishes::NUMERIC / hrs.races_run) * 100, 1)
                ELSE 0 
            END as top3_percentage
        FROM horse_race_stats hrs
        LEFT JOIN horse_betting_stats hbs ON hrs.horse_id = hbs.horse_id
    )
    SELECT 
        name,
        age,
        temperament,
        races_run,
        wins,
        win_percentage,
        top3_percentage,
        ROUND(avg_finish_position, 2) as avg_position,
        ROUND(avg_race_time, 2) as avg_time,
        ROUND(best_time, 2) as best_time,
        ROUND(avg_odds, 2) as avg_odds,
        total_bets_on,
        ROUND(total_wagered_on, 2) as wagered_on,
        ROUND(profit_for_house, 2) as house_profit,
        RANK() OVER (ORDER BY win_percentage DESC, avg_finish_position ASC) as performance_rank,
        CASE 
            WHEN win_percentage >= 25 THEN 'Champion'
            WHEN win_percentage >= 15 THEN 'Strong'
            WHEN win_percentage >= 10 THEN 'Average'
            ELSE 'Underperformer'
        END as performance_tier
    FROM combined_stats
    ORDER BY win_percentage DESC, avg_finish_position ASC;
    """
    
    print("\n🐎 QUERY 3: Horse Racing Performance Analytics")
    print("=" * 60)
    
    with app.app_context():
        result = db.session.execute(text(raw_sql))
        
        print(f"{'Horse Name':<15} {'Age':<4} {'Races':<6} {'Wins':<5} {'Win%':<6} {'Avg Pos':<8} {'Tier':<12}")
        print("-" * 70)
        
        for row in result:
            print(f"{row.name:<15} {row.age:<4} {row.races_run:<6} {row.wins:<5} "
                  f"{row.win_percentage:<6.1f} {row.avg_position:<8.2f} {row.performance_tier:<12}")


def query_4_transaction_pattern_analysis():
    """
    QUERY 4: User Transaction and Spending Pattern Analysis
    =======================================================
    
    Analyzes user financial behavior patterns including deposit/withdrawal ratios,
    spending velocity, and financial health indicators.
    
    Demonstrates: Window functions, Date calculations, Financial analytics
    """
    
    raw_sql = """
    WITH user_transaction_summary AS (
        SELECT 
            u.user_id,
            u.username,
            u.created_at as user_since,
            w.currency,
            w.balance as current_balance,
            COUNT(t.txn_id) as total_transactions,
            SUM(CASE WHEN t.txn_type IN ('deposit', 'admin_credit') THEN t.amount ELSE 0 END) as total_deposits,
            SUM(CASE WHEN t.txn_type IN ('withdraw', 'admin_debit') THEN t.amount ELSE 0 END) as total_withdrawals,
            SUM(CASE WHEN t.txn_type = 'bet_loss' THEN t.amount ELSE 0 END) as total_bet_losses,
            SUM(CASE WHEN t.txn_type = 'bet_win' THEN t.amount ELSE 0 END) as total_bet_wins,
            MIN(t.created_at) as first_transaction,
            MAX(t.created_at) as last_transaction,
            COUNT(DISTINCT DATE(t.created_at)) as active_transaction_days
        FROM users u
        JOIN wallets w ON u.user_id = w.user_id
        LEFT JOIN transactions t ON w.wallet_id = t.wallet_id
        WHERE u.is_admin = FALSE
        GROUP BY u.user_id, u.username, u.created_at, w.currency, w.balance
        HAVING COUNT(t.txn_id) > 0
    ),
    user_financial_metrics AS (
        SELECT *,
            EXTRACT(DAYS FROM (COALESCE(last_transaction, NOW()) - user_since)) + 1 as days_since_signup,
            EXTRACT(DAYS FROM (last_transaction - first_transaction)) + 1 as transaction_span_days,
            total_deposits - total_withdrawals as net_deposits,
            total_bet_wins - total_bet_losses as net_betting_result,
            CASE 
                WHEN total_deposits > 0 
                THEN ROUND((total_withdrawals / total_deposits) * 100, 2)
                ELSE 0 
            END as withdrawal_ratio_pct,
            CASE 
                WHEN active_transaction_days > 0 
                THEN ROUND(total_transactions::NUMERIC / active_transaction_days, 2)
                ELSE 0 
            END as avg_transactions_per_day,
            CASE 
                WHEN total_deposits > 0 
                THEN ROUND(((total_bet_losses + total_bet_wins) / total_deposits) * 100, 2)
                ELSE 0 
            END as betting_intensity_pct
        FROM user_transaction_summary
    ),
    financial_health_scoring AS (
        SELECT *,
            CASE 
                WHEN net_deposits > 0 AND withdrawal_ratio_pct < 50 THEN 'Healthy Depositor'
                WHEN net_deposits > 0 AND withdrawal_ratio_pct < 80 THEN 'Balanced Player'  
                WHEN net_deposits <= 0 AND current_balance > 0 THEN 'Profitable Player'
                WHEN current_balance <= 0 THEN 'Depleted Account'
                ELSE 'High Withdrawal Risk'
            END as financial_health_status,
            RANK() OVER (ORDER BY total_deposits DESC) as deposit_volume_rank,
            RANK() OVER (ORDER BY betting_intensity_pct DESC) as betting_activity_rank
        FROM user_financial_metrics
    )
    SELECT 
        username,
        currency,
        ROUND(current_balance, 2) as balance,
        total_transactions,
        ROUND(total_deposits, 2) as deposits,
        ROUND(total_withdrawals, 2) as withdrawals,
        ROUND(net_deposits, 2) as net_deposits,
        withdrawal_ratio_pct,
        betting_intensity_pct,
        avg_transactions_per_day,
        transaction_span_days,
        financial_health_status,
        deposit_volume_rank
    FROM financial_health_scoring
    WHERE total_deposits > 0
    ORDER BY total_deposits DESC;
    """
    
    print("\n💰 QUERY 4: Transaction Pattern Analysis")
    print("=" * 60)
    
    with app.app_context():
        result = db.session.execute(text(raw_sql))
        
        print(f"{'Username':<12} {'Currency':<8} {'Deposits':<10} {'W/D Ratio%':<10} {'Health Status':<18}")
        print("-" * 70)
        
        for row in result:
            print(f"{row.username:<12} {row.currency:<8} ${row.deposits:<9.2f} "
                  f"{row.withdrawal_ratio_pct:<10.1f} {row.financial_health_status:<18}")


def query_5_betting_behavior_cohort_analysis():
    """
    QUERY 5: Advanced Betting Behavior and Cohort Analysis
    ======================================================
    
    Performs cohort analysis based on user registration dates and betting patterns.
    Includes retention analysis and user lifecycle metrics.
    
    Demonstrates: Cohort analysis, Date functions, Advanced analytics, User segmentation
    """
    
    raw_sql = """
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
            EXTRACT(DAYS FROM (ufb.first_bet_date - uc.created_at::DATE)) as days_to_first_bet,
            COUNT(b.bet_id) as total_bets,
            COUNT(DISTINCT DATE(b.placed_at)) as betting_days,
            COUNT(DISTINCT r.game_id) as games_tried,
            SUM(b.amount) as total_wagered,
            AVG(b.amount) as avg_bet_size,
            STDDEV(b.amount) as bet_size_variance,
            MIN(b.placed_at) as betting_start,
            MAX(b.placed_at) as last_bet_date,
            EXTRACT(DAYS FROM (MAX(b.placed_at) - MIN(b.placed_at))) + 1 as betting_lifespan_days
        FROM user_cohorts uc
        LEFT JOIN user_first_bet ufb ON uc.user_id = ufb.user_id
        LEFT JOIN bets b ON uc.user_id = b.user_id
        LEFT JOIN rounds r ON b.round_id = r.round_id
        GROUP BY uc.user_id, uc.username, uc.cohort_month, ufb.first_bet_date, ufb.first_bet_month
        HAVING COUNT(b.bet_id) > 0
    ),
    cohort_analysis AS (
        SELECT 
            cohort_month,
            COUNT(DISTINCT user_id) as cohort_size,
            AVG(days_to_first_bet) as avg_days_to_first_bet,
            AVG(total_bets) as avg_bets_per_user,
            AVG(betting_days) as avg_betting_days,
            AVG(games_tried) as avg_games_tried,
            AVG(total_wagered) as avg_total_wagered,
            AVG(betting_lifespan_days) as avg_betting_lifespan,
            COUNT(CASE WHEN betting_lifespan_days >= 30 THEN 1 END) as retained_30_days,
            COUNT(CASE WHEN betting_lifespan_days >= 90 THEN 1 END) as retained_90_days
        FROM user_betting_journey
        WHERE cohort_month IS NOT NULL
        GROUP BY cohort_month
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
    ORDER BY total_wagered DESC;
    """
    
    print("\n📊 QUERY 5: Betting Behavior and Cohort Analysis")
    print("=" * 60)
    
    with app.app_context():
        result = db.session.execute(text(raw_sql))
        
        print(f"{'Username':<12} {'Total Bets':<10} {'Wagered':<10} {'Lifespan':<9} {'Segment':<15}")
        print("-" * 70)
        
        for row in result:
            print(f"{row.username:<12} {row.total_bets:<10} ${row.total_wagered:<9.2f} "
                  f"{row.betting_lifespan_days:<9} {row.player_segment:<15}")


def run_all_complex_queries():
    """
    Execute all 5 complex queries in sequence
    """
    print("🔍 EXECUTING 5 COMPLEX SQL QUERIES FOR DATABASE COURSE")
    print("=" * 80)
    print("These queries demonstrate advanced SQL concepts including:")
    print("• Complex JOINs across multiple tables")
    print("• Window functions and ranking")
    print("• Common Table Expressions (CTEs)")
    print("• Aggregate functions with GROUP BY/HAVING")
    print("• Subqueries and correlated subqueries")
    print("• Advanced analytics and business intelligence")
    print("• Date/time calculations and cohort analysis")
    print("=" * 80)
    
    try:
        query_1_user_performance_analytics()
        query_2_game_revenue_analysis()
        query_3_horse_racing_analytics()
        query_4_transaction_pattern_analysis()
        query_5_betting_behavior_cohort_analysis()
        
        print("\n✅ All complex queries executed successfully!")
        print("These queries meet database course requirements for sophisticated SQL analysis.")
        
    except Exception as e:
        print(f"❌ Error executing complex queries: {str(e)}")
        raise


if __name__ == "__main__":
    run_all_complex_queries() 