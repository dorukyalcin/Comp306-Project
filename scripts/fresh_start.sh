#!/bin/bash

# Fresh Start Script - Brings up site with comprehensive seed data
# This creates a complete testing environment with realistic data

echo "🚀 FRESH START SCRIPT - COMPLETE SITE INITIALIZATION"
echo "===================================================="
echo "🌱 This will create a fresh site with comprehensive test data:"
echo "   ✅ 12 Users (2 admins, 10 regular)"
echo "   ✅ Multi-currency wallets (USD, EUR, BTC)"
echo "   ✅ ALL WALLET BALANCES GUARANTEED POSITIVE"
echo "   ✅ 140+ realistic transactions"
echo "   ✅ 24 Racing horses with diverse characteristics"
echo "   ✅ 25 game rounds with betting history"
echo "   ✅ 15 sarcastic templates with user settings"
echo "   ✅ 6 casino games ready to play"
echo ""

# Ask for confirmation
read -p "Start fresh site initialization? (Y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Fresh start cancelled."
    exit 1
fi

echo ""
echo "🏗️  Step 1: Building and starting containers..."
docker-compose up -d --build

echo ""
echo "⏳ Step 2: Waiting for services to be ready..."
sleep 5

echo ""
echo "🌱 Step 3: Running clean database seeding with positive balances..."
docker-compose exec web python seeding/clean_seed.py <<EOF
yes
EOF

echo ""
echo "🔍 Step 4: Verifying database contents..."
echo "Database Summary:"
docker-compose exec web python -c "
import sys
sys.path.insert(0, '/app')
from app import app, db
from models import *
with app.app_context():
    print(f'👥 Users: {User.query.count()}')
    print(f'💰 Wallets: {Wallet.query.count()}')
    print(f'💳 Transactions: {Transaction.query.count()}')
    print(f'🎮 Games: {Game.query.count()}')
    print(f'🎯 Rounds: {Round.query.count()}')
    print(f'🎲 Bets: {Bet.query.count()}')
    print(f'😏 Sarcastic Templates: {SarcasTemp.query.count()}')
    print(f'🐎 Horses: {Horse.query.count()}')
    if Horse.query.count() > 0:
        print('🏁 Horse Racing System: READY')
    else:
        print('⚠️  Horse Racing System: NOT READY')
"

echo ""
echo "✅ FRESH START COMPLETE!"
echo "===================================================="
echo "🌐 Your sarcastic gambling site is ready!"
echo ""
echo "🔗 Access:"
echo "   Website: http://localhost:8000"
echo "   Horse Racing: http://localhost:8000/horse-racing"
echo "   Database: localhost:5432"
echo ""
echo "👤 Login Credentials:"
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
echo "🎮 Available Games:"
echo "   • 🐎 Enhanced Horse Racing (with 24 real horses!)"
echo "   • 🃏 Blackjack     • 🎰 Roulette"
echo "   • 🎰 Slot Machine  • 🎯 Plinko"
echo "   • 💣 Minesweeper"
echo ""
echo "🐎 Horse Racing Features:"
echo "   • 24 unique horses with realistic stats"
echo "   • Dynamic odds based on horse characteristics"
echo "   • Physics-based race simulation"
echo "   • Win/Place/Show betting options"
echo "   • Age range: 2-13 years, Speed range: 6.5-9.2"
echo ""
echo "💰 Financial Features:"
echo "   • Multi-currency wallets (USD, EUR, BTC)"
echo "   • Deposit/withdrawal system"
echo "   • Transaction history with filtering"
echo "   • Realistic starting balances"
echo ""
echo "😏 Sarcasm System:"
echo "   • 15 sarcastic templates"
echo "   • 5 severity levels (1-5)"
echo "   • Personalized user settings"
echo "   • 6 UI themes available"
echo ""
echo "🛠️  Development Commands:"
echo "   View all data: docker-compose run web python seeding/view_db.py"
echo "   Horse racing: ./scripts/dev_menu.sh (option 8)"
echo "   Stop safely:  docker-compose down"
echo "   Teardown all: ./scripts/teardown.sh"
echo "====================================================" 