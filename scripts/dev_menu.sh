#!/bin/bash

# Development Menu Script - Interactive menu for all development operations

echo "🎰 SARCASTIC GAMBLING SITE - DEVELOPMENT MENU"
echo "=============================================="
echo "Choose an operation:"
echo ""
echo "🚀 SITE MANAGEMENT:"
echo "1) Fresh Start        - Complete fresh site with full test data"
echo "2) Safe Restart       - Restart containers, preserve data"
echo "3) Teardown           - Destroy everything (DANGER!)"
echo ""
echo "🌱 DATA MANAGEMENT:"
echo "4) Seed Data Only     - Add comprehensive data to existing DB"
echo "5) Clean Seed         - Reset DB with guaranteed positive balances"
echo "6) Balance Check      - Quick check of wallet balances"
echo "7) Quick View         - Show current database status"
echo ""
echo "🐎 HORSE RACING:"
echo "10) Horse Racing View - Show detailed horse racing data"
echo "11) Seed Horses Only  - Add only horse data to database"
echo ""
echo "🔧 DIRECT COMMANDS:"
echo "8) View All Data      - Detailed database inspection"
echo "9) Reset DB Only      - Reset database only (keep containers)"
echo ""
echo "🛠️  TROUBLESHOOTING:"
echo "12) Fix Missing Wallets - Create wallets for users without them"
echo ""
echo "0) Exit"
echo ""
read -p "Enter your choice (0-12): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Running Fresh Start..."
        ./scripts/fresh_start.sh
        ;;
    2)
        echo ""
        echo "🔄 Running Safe Restart..."
        ./scripts/safe_restart.sh
        ;;
    3)
        echo ""
        echo "🔥 Running Teardown..."
        ./scripts/teardown.sh
        ;;
    4)
        echo ""
        echo "🌱 Running Seed Data Only..."
        ./scripts/seed_only.sh
        ;;
    5)
        echo ""
        echo "🧹 Running Clean Seed..."
        ./scripts/clean_seed.sh
        ;;
    6)
        echo ""
        echo "💰 Running Balance Check..."
        ./scripts/balance_check.sh
        ;;
    7)
        echo ""
        echo "🔍 Running Quick View..."
        ./scripts/quick_view.sh
        ;;
    8)
        echo ""
        echo "📋 Viewing All Database Data..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose run --rm web python seeding/view_db.py
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    9)
        echo ""
        echo "🔄 Resetting Database Only..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose run --rm web python seeding/reset_db.py
            echo "✅ Database reset complete!"
            echo "💡 Run option 4 to add comprehensive seed data."
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    10)
        echo ""
        echo "🐎 Viewing Horse Racing Data..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose exec web python -c "
import sys
sys.path.insert(0, '/app')
from app import app, db
from models import *
from games import HorseRacing
with app.app_context():
    hr = HorseRacing()
    print('🐎 HORSE RACING SYSTEM STATUS')
    print('=' * 40)
    print(f'🐴 Total Horses: {Horse.query.count()}')
    print(f'🏁 Active Race Runners: {HorseRunner.query.count()}')
    print(f'🏆 Completed Race Results: {HorseResult.query.count()}')
    print()
    if Horse.query.count() > 0:
        print('🌟 Sample Horses:')
        for horse in Horse.query.limit(5):
            print(f'   • {horse.name} (Age: {horse.age}, Speed: {horse.base_speed}, {horse.temperament.title()})')
        print()
        active_round = hr.get_active_round()
        if active_round:
            print(f'🏁 ACTIVE RACE: Round {active_round.round_id}')
        else:
            print('✨ No active race - ready to start new race!')
        print()
        print('🎯 Game Configuration:')
        game = hr.get_game()
        if game:
            print(f'   Min Bet: {game.min_bet} | Max Bet: {game.max_bet}')
            print(f'   House Edge: {game.house_edge * 100}%')
        print()
        validation = hr.validate_game_setup()
        if validation['valid']:
            print('✅ Horse Racing System: READY')
        else:
            print(f'❌ Horse Racing System: {validation[\"message\"]}')
    else:
        print('⚠️  No horses found! Run option 9 to seed horses.')
    print('=' * 40)
"
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    11)
        echo ""
        echo "🐎 Seeding Horses Only..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose run --rm web python seeding/seed_horses.py
            echo "✅ Horse seeding complete!"
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    12)
        echo ""
        echo "🛠️  Fixing Missing Wallets..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose run --rm web python seeding/fix_missing_wallets.py
            echo "✅ Wallet fix complete!"
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    0)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run again and select 0-12."
        exit 1
        ;;
esac

echo ""
echo "🎯 Operation completed!"
echo "💡 Run './scripts/dev_menu.sh' again for more operations."
echo "🌐 Site URL: http://localhost:8000"
echo "🐎 Horse Racing: http://localhost:8000/horse-racing"
echo "==============================================" 