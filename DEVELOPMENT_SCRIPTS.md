# Development Scripts Guide

## Quick Commands for Site Management

I've created comprehensive scripts to manage your development workflow with enhanced horse racing functionality:

## 🔥 `./scripts/teardown.sh` - Complete Site Teardown

**Purpose:** Completely shuts down the site and deletes ALL database data.

**What it does:**
- Stops all Docker containers
- Removes all Docker volumes (deletes database data)
- Cleans up orphaned containers
- Removes unused Docker resources

**Usage:**
```bash
./scripts/teardown.sh
```

**⚠️ WARNING:** This deletes EVERYTHING:
- All user accounts
- All wallet balances
- All transaction history
- All game rounds and bets
- All 24 horses and race results
- All sarcastic templates
- Complete database wipe

## 🚀 `./scripts/fresh_start.sh` - Fresh Site with Full Data

**Purpose:** Brings up a fresh site with comprehensive seed data including enhanced horse racing.

**What it creates:**
- **12 Users** (2 admins + 10 regular users)
- **22 Multi-currency wallets** (USD, EUR, BTC)
- **142+ Realistic transactions** (deposits, withdrawals, wins, losses)
- **24 Racing horses** with diverse characteristics (ages 2-13, speeds 6.5-9.2)
- **29 Game rounds** with betting history
- **98 Realistic bets** across all games
- **15 Sarcastic templates** with 5 severity levels
- **12 User settings** with personalized themes

**Usage:**
```bash
./scripts/fresh_start.sh
```

**Total money created:**
- ~$4,800+ USD
- ~€100M+ EUR  
- ~₿0.6+ BTC

## 🐎 Horse Racing System

### Enhanced Features:
- **24 Unique horses** with realistic names and characteristics
- **Dynamic odds calculation** based on horse age, speed, and temperament
- **Physics-based race simulation** for realistic results
- **Multiple bet types:** Win, Place, Show
- **Complete race history** with finishing times and positions

### Horse Characteristics:
- **Age Range:** 2-13 years (affects performance)
- **Speed Range:** 6.5-9.2 (base racing speed)
- **Temperaments:** Confident, Aggressive, Nervous, Calm, Unpredictable

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

# 2. Start fresh with full data (includes horses)
./scripts/fresh_start.sh

# 3. Visit http://localhost:8000
# 4. Try horse racing at http://localhost:8000/horse-racing
```

### Interactive Menu (Easiest):
```bash
# Use the interactive menu for all operations
./scripts/dev_menu.sh

# New horse racing options:
# Option 8: View horse racing system status
# Option 9: Seed horses only
```

### Safe Restart (Preserves All Data):
```bash
# Restart containers while preserving horse data
./scripts/safe_restart.sh
```

### Quick Status Check:
```bash
# View database status including horse racing
./scripts/quick_view.sh
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
- `horse_henry` - Horse betting expert (perfect for testing horse racing!)
- `mine_mary` - Minesweeper champion
- `newbie_nick` - New player learning

## 🛠️ Useful Commands

### View Database Contents:
```bash
docker-compose run web python seeding/view_db.py
```

### Horse Racing Specific:
```bash
# Check horse racing system status
./scripts/dev_menu.sh  # Select option 8

# Seed only horses (if missing)
./scripts/dev_menu.sh  # Select option 9

# Or directly:
docker-compose run web python seeding/seed_horses.py
```

### Run Individual Seeding:
```bash
# Just create tables
docker-compose run web python seeding/init_db.py

# Just add games
docker-compose run web python seeding/seed_games.py

# Full comprehensive seeding (includes horses)
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
| Wallets | 22 | Multi-currency per user |
| Transactions | 142 | Realistic financial activity |
| Games | 6 | All casino games (including enhanced horse racing) |
| Rounds | 29 | Game sessions |
| Bets | 98 | User betting activity |
| Outcomes | 29 | Game results |
| **Horses** | **24** | **Unique racing horses with stats** |
| **Horse Runners** | **Variable** | **Horses in active/past races** |
| **Horse Results** | **Variable** | **Race finishing data** |
| User Settings | 12 | Personalized preferences |
| Sarcastic Templates | 15 | Funny messages |

## 🎯 Testing Scenarios

After running `./scripts/fresh_start.sh`, you can test:

1. **Authentication:** Login with any user
2. **Multi-currency:** Check different wallet currencies
3. **Transactions:** Filter transaction history
4. **🐎 Horse Racing:** 
   - Start new races with 6 random horses
   - Place Win/Place/Show bets
   - Watch physics-based race simulation
   - View race results and payouts
5. **Gaming:** Place bets on different games
6. **Sarcasm:** Experience different sarcasm levels
7. **Admin:** Use admin accounts for management
8. **Themes:** Switch between UI themes

## 🐎 Horse Racing Testing Guide

### Test the Enhanced Horse Racing:
1. **Login** as `horse_henry` (perfect test user!)
2. **Visit** `/horse-racing`
3. **Start New Race** - see 6 randomly selected horses
4. **Check Horse Stats** - age, speed, temperament affect odds
5. **Place Bets** - try Win (1st), Place (1st-2nd), Show (1st-3rd)
6. **Run Race** - watch physics-based simulation
7. **View Results** - see finishing positions and times
8. **Check Payouts** - automatic calculation based on original odds

### Horse Racing Features to Test:
- **Dynamic Odds:** Notice how horse characteristics affect betting odds
- **Race Variety:** Each race has different horses and outcomes
- **Bet Types:** Test all three betting options
- **Realistic Simulation:** Horses perform based on their stats
- **Complete History:** All races are recorded in the database

This setup provides a complete, realistic testing environment for your gambling site with a sophisticated horse racing system!

## 🔍 Troubleshooting

### Horse Racing Not Working:
```bash
# Check horse racing system status
./scripts/dev_menu.sh  # Option 8

# If no horses found, seed them:
./scripts/dev_menu.sh  # Option 9
```

### Complete Reset:
```bash
./scripts/teardown.sh     # Nuclear option
./scripts/fresh_start.sh  # Fresh start with all data
``` 