#!/bin/bash

# Safe Restart Script - Restarts containers while preserving database data

echo "🔄 SAFE RESTART - PRESERVING DATA"
echo "================================="
echo "This will restart the site while keeping all database data:"
echo "   ✅ User accounts preserved"
echo "   ✅ Wallet balances preserved" 
echo "   ✅ Transaction history preserved"
echo "   ✅ Game history preserved"
echo "   ✅ Horse racing data preserved (24 horses + race results)"
echo "   ✅ All settings preserved"
echo ""

read -p "Proceed with safe restart? (Y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ Safe restart cancelled."
    exit 1
fi

echo ""
echo "🛑 Stopping containers..."
docker-compose down

echo ""
echo "🚀 Starting containers..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "🔍 Verifying site status..."
docker-compose ps

echo ""
echo "✅ SAFE RESTART COMPLETE!"
echo "================================="
echo "🌐 Your site is running with preserved data!"
echo "   Website: http://localhost:8000"
echo "   Horse Racing: http://localhost:8000/horse-racing"
echo ""
echo "💡 To check your data:"
echo "   ./scripts/quick_view.sh"
echo "   ./scripts/dev_menu.sh (option 8 for horse racing)"
echo "=================================" 