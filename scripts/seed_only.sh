#!/bin/bash

# Seed Only Script - Adds comprehensive data to existing database
# Safe to run - won't duplicate data if it already exists

echo "🌱 COMPREHENSIVE SEEDING ONLY"
echo "============================="
echo "This will add comprehensive test data to your existing database:"
echo "   • 12 Users (if database is empty)"
echo "   • Multi-currency wallets"
echo "   • ✅ ALL WALLET BALANCES GUARANTEED POSITIVE"
echo "   • Realistic transactions"
echo "   • 24 Racing horses with diverse characteristics"
echo "   • Game rounds and betting history"
echo "   • Sarcastic templates and user settings"
echo ""
echo "⚠️  Note: Will skip seeding if users already exist"
echo ""

# Ask for confirmation
read -p "Run comprehensive seeding? (Y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Seeding cancelled."
    exit 1
fi

echo ""
echo "🔍 Checking container status..."
docker-compose ps

echo ""
echo "🎮 Ensuring casino games are set up..."
docker-compose exec web python seeding/seed_games.py

echo ""
echo "🌱 Running comprehensive seeding with positive balances..."
docker-compose exec web python seeding/comprehensive_seed.py

echo ""
echo "🐎 Setting up horse racing data..."
docker-compose exec web python seeding/seed_horses.py
docker-compose exec web python seeding/seed_horse_races.py

echo ""
echo "🔍 Verifying wallet balances..."
docker-compose exec web python -c "import sys; sys.path.insert(0, '/app'); from app import app, db; from models import *; app.app_context().push(); total_wallets = Wallet.query.count(); negative_wallets = Wallet.query.filter(Wallet.balance < 0).count(); print(f'💰 Total wallets: {total_wallets}'); print(f'✅ ALL WALLETS HAVE POSITIVE BALANCES!' if negative_wallets == 0 else f'⚠️ WARNING: {negative_wallets} wallets have negative balances')"

echo ""
echo "📊 Final database status:"
docker-compose exec web python -c "import sys; sys.path.insert(0, '/app'); from app import app, db; from models import *; app.app_context().push(); print(f'👥 Users: {User.query.count()}'); print(f'💰 Wallets: {Wallet.query.count()}'); print(f'💳 Transactions: {Transaction.query.count()}'); print(f'🎮 Games: {Game.query.count()}'); print(f'🎯 Rounds: {Round.query.count()}'); print(f'🎲 Bets: {Bet.query.count()}'); print(f'🐎 Horses: {Horse.query.count()}'); print(f'🏁 Horse Runners: {HorseRunner.query.count()}'); print(f'🏆 Horse Results: {HorseResult.query.count()}'); print('🎯 Horse Racing Ready!' if Horse.query.count() > 0 else '⚠️ No horses found - run horse seeding script')"

echo ""
echo "✅ SEEDING COMPLETE!"
echo "============================="
echo "🌐 Visit: http://localhost:8000"
echo "👤 Login: Any username with password 'password123'"
echo "🐎 Try the enhanced horse racing at: /horse-racing"
echo "=============================" 