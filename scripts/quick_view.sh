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
    print('🐎 Horse Racing System:')
    print(f'   🐴 Horses: {Horse.query.count()}')
    print(f'   🏁 Active Race Runners: {HorseRunner.query.count()}')
    print(f'   🏆 Race Results: {HorseResult.query.count()}')
    if Horse.query.count() > 0:
        avg_age = db.session.query(db.func.avg(Horse.age)).scalar()
        avg_speed = db.session.query(db.func.avg(Horse.base_speed)).scalar()
        print(f'   📊 Average Horse Age: {avg_age:.1f} years')
        print(f'   📊 Average Horse Speed: {avg_speed:.1f}')
        print(f'   🎯 Speed Range: {Horse.query.order_by(Horse.base_speed.desc()).first().base_speed} - {Horse.query.order_by(Horse.base_speed.asc()).first().base_speed}')
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