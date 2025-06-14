#!/bin/bash

# Teardown Script - Completely removes site and deletes all database data
# WARNING: This will delete ALL data including users, transactions, etc.

echo "🔥 TEARDOWN SCRIPT - COMPLETE SITE SHUTDOWN"
echo "=========================================="
echo "⚠️  WARNING: This will DELETE ALL DATABASE DATA!"
echo "   - All users will be removed"
echo "   - All transactions will be deleted"
echo "   - All game history will be lost"
echo "   - All wallet balances will be reset"
echo "   - All 24 horses and race results will be deleted"
echo ""

# Ask for confirmation
read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Teardown cancelled."
    exit 1
fi

echo ""
echo "🛑 Taking down all containers..."
docker-compose down

echo ""
echo "🗑️  Removing all volumes (this deletes the database data)..."
docker-compose down -v

echo ""
echo "🧹 Cleaning up orphaned containers..."
docker-compose down --remove-orphans

echo ""
echo "🧽 Removing unused Docker resources..."
docker system prune -f

echo ""
echo "✅ TEARDOWN COMPLETE!"
echo "=========================================="
echo "📊 Status:"
echo "   - All containers: STOPPED"
echo "   - All volumes: DELETED"
echo "   - All database data: DELETED"
echo "   - All user accounts: DELETED"
echo "   - All horse racing data: DELETED"
echo ""
echo "💡 To bring the site back up with fresh data, run:"
echo "   ./scripts/fresh_start.sh"
echo "==========================================" 