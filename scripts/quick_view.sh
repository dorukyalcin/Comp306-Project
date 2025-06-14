#!/bin/bash

# Quick View Script - Shows database status without modifying data
# Safe read-only database inspection

echo "🔍 QUICK DATABASE & SITE STATUS"
echo "==============================="

echo "📊 Container Status:"
docker-compose ps

echo ""
echo "💾 Database Summary:"
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
    print(f'📝 Outcomes: {Outcome.query.count()}')
    print(f'⚙️  User Settings: {UserSettings.query.count()}')
    print(f'😏 Sarcastic Templates: {SarcasTemp.query.count()}')
    print()
    print('👤 Sample Users:')
    for user in User.query.limit(3):
        role = 'Admin' if user.is_admin else 'Regular'
        print(f'   • {user.username} ({role})')
    print()
    print('💰 Total Money in System:')
    for currency in ['USD', 'EUR', 'BTC']:
        total = db.session.query(db.func.sum(Wallet.balance)).filter_by(currency=currency).scalar() or 0
        if currency == 'BTC':
            print(f'   {currency}: ₿{total}')
        elif currency == 'EUR':
            print(f'   {currency}: €{total}')
        else:
            print(f'   {currency}: \${total}')
"

echo ""
echo "🌐 Site Access:"
echo "   Website: http://localhost:8000"
echo "   Password for all users: password123"
echo "===============================" 