#!/bin/bash

# Balance Check Script - Quick utility to check wallet balances
# Safe to run - only checks data, doesn't modify anything

echo "💰 WALLET BALANCE CHECK"
echo "======================="

echo ""
echo "🔍 Checking container status..."
if ! docker-compose ps | grep -q "web.*Up"; then
    echo "❌ Web container is not running!"
    echo "Start with: docker-compose up -d"
    exit 1
fi

echo ""
echo "📊 Current wallet balance status:"
docker-compose exec web python seeding/clean_seed.py --check

echo ""
echo "💡 Quick Actions:"
echo "   Fix negative balances: ./scripts/clean_seed.sh"
echo "   View detailed data:    docker-compose exec web python seeding/view_db.py"
echo "   Admin dashboard:       http://localhost:8000/admin"
echo "=======================" 