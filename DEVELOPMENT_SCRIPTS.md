# Development Scripts Guide

## Quick Commands for Site Management

I've created two convenient scripts to manage your development workflow:

## 🔥 `./teardown.sh` - Complete Site Teardown

**Purpose:** Completely shuts down the site and deletes ALL database data.

**What it does:**
- Stops all Docker containers
- Removes all Docker volumes (deletes database data)
- Cleans up orphaned containers
- Removes unused Docker resources

**Usage:**
```bash
./teardown.sh
```

**⚠️ WARNING:** This deletes EVERYTHING:
- All user accounts
- All wallet balances
- All transaction history
- All game rounds and bets
- All sarcastic templates
- Complete database wipe

## 🚀 `./fresh_start.sh` - Fresh Site with Full Data

**Purpose:** Brings up a fresh site with comprehensive seed data.

**What it creates:**
- **12 Users** (2 admins + 10 regular users)
- **26 Multi-currency wallets** (USD, EUR, BTC)
- **140+ Realistic transactions** (deposits, withdrawals, wins, losses)
- **25 Game rounds** with betting history
- **98 Realistic bets** across all games
- **15 Sarcastic templates** with 5 severity levels
- **12 User settings** with personalized themes

**Usage:**
```bash
./fresh_start.sh
```

**Total money created:**
- ~$4,000-5,000 USD
- ~€3,000-4,000 EUR  
- ~₿3-4 BTC

## 🔄 Development Workflow

### First Time Setup (After Cloning Repository):
```bash
# Make all scripts executable
chmod +x scripts/*.sh
```

### Complete Reset and Fresh Start:
```bash
# 1. Tear down everything
./scripts/teardown.sh

# 2. Start fresh with full data
./scripts/fresh_start.sh

# 3. Visit http://localhost:8000
```

### Interactive Menu (Easiest):
```bash
# Use the interactive menu for all operations
./scripts/dev_menu.sh
```

### Safe Stop (Preserves Data):
```bash
# Just stop containers, keep data
docker-compose down
```

### Quick Restart (Preserves Data):
```bash
# Restart existing containers
docker-compose up -d
```

## 👤 Login Credentials (After Fresh Start)

**All users have password:** `password123`

### Admin Users:
- `admin_casino`
- `admin_sarah`

### Regular Users:
- `lucky_mike` - Horse racing enthusiast
- `gambler_jane` - High roller
- `risk_taker_bob` - Aggressive player
- `slot_queen_amy` - Slot machine lover
- `blackjack_tom` - Card game expert
- `roulette_lisa` - European roulette player
- `plinko_pete` - Plinko specialist
- `horse_henry` - Horse betting expert
- `mine_mary` - Minesweeper champion
- `newbie_nick` - New player learning

## 🛠️ Useful Commands

### View Database Contents:
```bash
docker-compose run web python seeding/view_db.py
```

### Run Individual Seeding:
```bash
# Just create tables
docker-compose run web python seeding/init_db.py

# Just add games
docker-compose run web python seeding/seed_games.py

# Full comprehensive seeding
docker-compose run web python seeding/comprehensive_seed.py
```

### Check Container Status:
```bash
docker-compose ps
```

### View Container Logs:
```bash
docker-compose logs web
docker-compose logs db
```

## 📊 Expected Data After Fresh Start

| Entity | Count | Description |
|--------|-------|-------------|
| Users | 12 | 2 admins, 10 regular users |
| Wallets | ~26 | Multi-currency per user |
| Transactions | ~143 | Realistic financial activity |
| Games | 6 | All casino games |
| Rounds | 25 | Game sessions |
| Bets | ~98 | User betting activity |
| Outcomes | 25 | Game results |
| User Settings | 12 | Personalized preferences |
| Sarcastic Templates | 15 | Funny messages |

## 🎯 Testing Scenarios

After running `./fresh_start.sh`, you can test:

1. **Authentication:** Login with any user
2. **Multi-currency:** Check different wallet currencies
3. **Transactions:** Filter transaction history
4. **Gaming:** Place bets on different games
5. **Sarcasm:** Experience different sarcasm levels
6. **Admin:** Use admin accounts for management
7. **Themes:** Switch between UI themes

This setup provides a complete, realistic testing environment for your gambling site! 