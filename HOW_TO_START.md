# How to Start the Sarcastic Casino Platform

## Quick Start

```bash
# 1. Take down any existing containers and clean volumes
docker-compose down -v

# 2. Build and start containers
docker-compose up --build -d

# 3. Wait for database initialization (10 seconds) and seed data
sleep 10 && docker-compose exec web python seeding/startup_with_seed.py

# 4. Visit http://localhost:8000
```

## Login Credentials

### Admin Users
- Username: `admin_casino` or `admin_sarah`
- Password: `password123`

### Regular Users
Choose any of these usernames:
- `lucky_mike` (general testing)
- `gambler_jane` (high roller)
- `risk_taker_bob` (aggressive player)
- `slot_queen_amy` (slot machine lover)
- `blackjack_tom` (card game expert)
- `roulette_lisa` (European roulette player)
- `plinko_pete` (Plinko specialist)
- `horse_henry` (horse betting expert)
- `mine_mary` (Minesweeper champion)
- `newbie_nick` (new player)

Password for all users: `password123`

## What Gets Seeded

After seeding, the system contains:
- 12 Users (2 admins, 10 regular users)
- 32 Wallets with multiple currencies
- 182 Transactions
- 6 Games
- 28 Game rounds
- 106 Bets
- 24 Horses
- 18 Horse races with results
- 15 Sarcastic templates

## Initial Balance Overview
- USD: $21,773.24
- EUR: €19,159.59
- BTC: ₿4.8417

## Troubleshooting

### 1. If the site doesn't load
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs web
docker-compose logs db
```

### 2. If database seeding fails
```bash
# Complete reset and restart
docker-compose down -v
docker-compose up --build -d
sleep 10
docker-compose exec web python seeding/startup_with_seed.py
```

### 3. To view database contents
```bash
# Check database status
docker-compose exec web python seeding/view_db.py
```

## Development Commands

### Container Management
```bash
# Stop containers
docker-compose stop

# Start existing containers
docker-compose start

# View real-time logs
docker-compose logs -f
```

### Database Management
```bash
# Reset database only
docker-compose exec web python seeding/reset_db.py

# View database structure
docker-compose exec web python check_db.py
```

## Important URLs

- Main Site: http://localhost:8000
- Admin Dashboard: http://localhost:8000/admin
- Games:
  - Horse Racing: http://localhost:8000/horse-racing
  - Blackjack: http://localhost:8000/blackjack
  - Slots: http://localhost:8000/slots
  - Plinko: http://localhost:8000/plinko
- User Profile: http://localhost:8000/profile
- Wallet Management: http://localhost:8000/wallet

## System Requirements

- Docker Engine 20.10.0+
- Docker Compose 2.0.0+
- At least 2GB of free RAM
- At least 5GB of free disk space
- Available ports:
  - 8000 (Web server)
  - 5432 (PostgreSQL) 