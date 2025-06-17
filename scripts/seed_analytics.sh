#!/bin/bash

# Seed Analytics Data Script
# =========================
# This script seeds data for all 5 analytics queries:
# 1. Game Performance Analysis
# 2. User Activity Patterns
# 3. Transaction Analysis
# 4. Retention Metrics
# 5. Betting Behavior Cohort Analysis

echo "🌱 Starting Analytics Data Seeding..."
echo "===================================="

# Function to handle errors
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Reset database first
echo "\n1️⃣  Resetting database..."
echo "DELETE ALL DATA" | python3 seeding/reset_db.py || handle_error "Database reset failed"

# Create admin users first
echo "\n2️⃣  Creating admin users..."
python3 seeding/comprehensive_seed.py || handle_error "Admin user creation failed"

# Seed games (required for all queries)
echo "\n3️⃣  Seeding games..."
python3 seeding/seed_games.py || handle_error "Game seeding failed"

# Create user cohorts (for Query 5)
echo "\n4️⃣  Seeding user cohorts and betting patterns..."
python3 seeding/seed_user_cohorts.py || handle_error "User cohort seeding failed"

# Seed horse racing data (for game variety)
echo "\n5️⃣  Seeding horse racing data..."
python3 seeding/seed_horses.py || handle_error "Horse seeding failed"
python3 seeding/seed_horse_races.py || handle_error "Horse race seeding failed"

# Enhance transactions (for Query 3)
echo "\n6️⃣  Enhancing transaction data..."
python3 seeding/enhance_transactions.py || handle_error "Transaction enhancement failed"

echo "\n✅ Analytics data seeding completed!"
echo "===================================="
echo "You can now view all 5 analytics queries in the admin dashboard."
echo "Login with:"
echo "  Username: admin_casino"
echo "  Password: password123" 