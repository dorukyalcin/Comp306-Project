#!/bin/bash

# Clean Seed Script - Complete database reset with guaranteed positive wallet balances
# This will completely reset and reseed with improved financial data

echo "🧹 CLEAN DATABASE SEEDING"
echo "========================="
echo "This will completely reset your database and create fresh seed data:"
echo "   🗑️  Drop all existing tables"
echo "   🏗️  Create fresh database schema"
echo "   👥 12 Users (2 admins, 10 regular)"
echo "   💰 Multi-currency wallets (USD, EUR, BTC)"
echo "   ✅ ALL WALLET BALANCES GUARANTEED POSITIVE"
echo "   💳 Realistic transaction history"
echo "   🐎 24 Racing horses with diverse characteristics"
echo "   🎯 Game rounds and betting history"
echo "   😏 Sarcastic templates and user settings"
echo ""
echo "⚠️  WARNING: This will DELETE all existing data!"
echo ""

# Ask for confirmation
read -p "Are you sure you want to proceed? (type 'yes' to confirm): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Clean seeding cancelled."
    exit 1
fi

echo ""
echo "🔍 Checking container status..."
docker-compose ps

echo ""
echo "🧹 Running clean database seeding with positive balances..."
echo "yes" | docker-compose exec -T web python seeding/clean_seed.py

echo ""
echo "🎮 Setting up casino games..."
docker-compose exec web python seeding/seed_games.py

echo ""
echo "🐎 Setting up horse racing data..."
docker-compose exec web python seeding/seed_horses.py
docker-compose exec web python seeding/seed_horse_races.py

echo ""
echo "🔍 Verifying positive wallet balances..."
docker-compose exec web python seeding/view_db.py

echo ""
echo "📊 Final database summary:"
docker-compose exec web python -c "import sys; sys.path.insert(0, '/app'); from app import app, db; from models import *; app.app_context().push(); print(f'👥 Users: {User.query.count()}'); print(f'💰 Wallets: {Wallet.query.count()}'); print(f'💳 Transactions: {Transaction.query.count()}'); print(f'🎮 Games: {Game.query.count()}'); print(f'🎯 Rounds: {Round.query.count()}'); print(f'🎲 Bets: {Bet.query.count()}'); print(f'🐎 Horses: {Horse.query.count()}')"

echo ""
echo "✅ CLEAN SEEDING COMPLETE!"
echo "========================="
echo "🌐 Website: http://localhost:8000"
echo "👤 Login credentials:"
echo "   Username: Any from the list below"
echo "   Password: password123"
echo ""
echo "🔧 ADMIN USERS:"
echo "   • admin_casino"
echo "   • admin_sarah"
echo ""
echo "👥 REGULAR USERS:"
echo "   • lucky_mike       • gambler_jane"
echo "   • risk_taker_bob   • slot_queen_amy"
echo "   • blackjack_tom    • roulette_lisa"
echo "   • plinko_pete      • horse_henry"
echo "   • mine_mary        • newbie_nick"
echo ""
echo "💰 ALL USERS NOW HAVE POSITIVE WALLET BALANCES!"
echo "   USD: $100 - $5000"
echo "   EUR: €80 - €4000"
echo "   BTC: 0.02 - 3.0"
echo ""
echo "🎮 Available Games:"
echo "   • 🐎 Horse Racing  • 🃏 Blackjack"
echo "   • 🎰 Slots         • 🎯 Plinko"
echo ""
echo "🛠️  Quick Commands:"
echo "   Check balances: ./scripts/balance_check.sh"
echo "   View all data:  docker-compose exec web python seeding/view_db.py"
echo "   Stop safely:    docker-compose down"
echo "=========================" 