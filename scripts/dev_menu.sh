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
echo "5) Quick View         - Show current database status"
echo ""
echo "🔧 DIRECT COMMANDS:"
echo "6) View All Data      - Detailed database inspection"
echo "7) Reset DB Only      - Reset database only (keep containers)"
echo ""
echo "0) Exit"
echo ""
read -p "Enter your choice (0-7): " choice

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
        echo "🔍 Running Quick View..."
        ./scripts/quick_view.sh
        ;;
    6)
        echo ""
        echo "📋 Viewing All Database Data..."
        if docker-compose ps | grep -q "Up"; then
            docker-compose run --rm web python seeding/view_db.py
        else
            echo "❌ Containers not running. Start them first with option 1 or 2."
        fi
        ;;
    7)
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
    0)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run again and select 0-7."
        exit 1
        ;;
esac

echo ""
echo "🎯 Operation completed!"
echo "💡 Run './scripts/dev_menu.sh' again for more operations."
echo "🌐 Site URL: http://localhost:8000"
echo "==============================================" 