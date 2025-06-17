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
docker-compose exec web python seeding/clean_seed.py <<EOF
yes
EOF

echo ""
echo "🔍 Verifying positive wallet balances..."
docker-compose exec web python -c "
import sys
sys.path.insert(0, '/app')
from app import app, db
from models import *
with app.app_context():
    total_wallets = Wallet.query.count()
    negative_wallets = Wallet.query.filter(Wallet.balance < 0).count()
    positive_wallets = total_wallets - negative_wallets
    
    print(f'📊 WALLET BALANCE VERIFICATION:')
    print(f'   Total wallets: {total_wallets}')
    print(f'   Positive balances: {positive_wallets}')
    print(f'   Negative balances: {negative_wallets}')
    
    if negative_wallets == 0:
        print(f'   ✅ ALL WALLETS HAVE POSITIVE BALANCES!')
    else:
        print(f'   ⚠️  WARNING: {negative_wallets} wallets have negative balances')
    
    print(f'\\n📈 BALANCE RANGES:')
    for currency in ['USD', 'EUR', 'BTC']:
        wallets = Wallet.query.filter_by(currency=currency).all()
        if wallets:
            balances = [float(w.balance) for w in wallets]
            min_bal = min(balances)
            max_bal = max(balances)
            avg_bal = sum(balances) / len(balances)
            print(f'   {currency}: {len(wallets)} wallets, Range: {min_bal:.2f} - {max_bal:.2f}, Avg: {avg_bal:.2f}')
"

echo ""
echo "📊 Final database summary:"
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
"

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