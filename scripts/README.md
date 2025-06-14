# Development Scripts

This directory contains all development scripts for the Sarcastic Gambling Site project.

## 🎯 Quick Start

### First Time Setup (After Cloning)
```bash
# Make all scripts executable
chmod +x scripts/*.sh
```

### Interactive Menu (Recommended)
```bash
./scripts/dev_menu.sh
```
This provides an interactive menu with all available operations.

## 📁 Available Scripts

### 🚀 **Site Management Scripts**

#### `fresh_start.sh` - Complete Fresh Start
- **Purpose:** Creates a completely fresh site with comprehensive test data
- **What it does:**
  - Builds and starts Docker containers
  - Creates database tables
  - Seeds games catalog
  - Adds comprehensive test data (12 users, 24 horses, transactions, bets, sarcasm system)
- **Usage:** `./scripts/fresh_start.sh`
- **Result:** Full testing environment with ~400 database records

#### `safe_restart.sh` - Safe Container Restart
- **Purpose:** Restarts containers while preserving all database data
- **What it does:**
  - Stops containers gracefully
  - Rebuilds and restarts containers
  - Preserves all user data, transactions, horses, etc.
- **Usage:** `./scripts/safe_restart.sh`
- **Safe:** No data loss

#### `teardown.sh` - Complete Teardown
- **Purpose:** Completely destroys site and deletes ALL data
- **What it does:**
  - Stops all containers
  - Removes all Docker volumes
  - Deletes all database data
  - Cleans up Docker resources
- **Usage:** `./scripts/teardown.sh`
- **⚠️ WARNING:** Destructive! Deletes everything

### 🌱 **Data Management Scripts**

#### `seed_only.sh` - Comprehensive Seeding Only
- **Purpose:** Adds comprehensive test data to existing database
- **What it does:**
  - Checks if containers are running
  - Runs comprehensive seeding script (including 24 horses)
  - Skips if users already exist
- **Usage:** `./scripts/seed_only.sh`
- **Safe:** Won't duplicate data

#### `quick_view.sh` - Quick Status Check
- **Purpose:** Shows current database status and site health
- **What it does:**
  - Shows container status
  - Displays database record counts
  - Shows horse racing system status
  - Shows sample users and total money
- **Usage:** `./scripts/quick_view.sh`
- **Fast:** Quick overview without detailed data

### 🐎 **Horse Racing Scripts**

#### `dev_menu.sh` Option 8 - Horse Racing View
- **Purpose:** Shows detailed horse racing system status
- **What it does:**
  - Displays all horses with their stats
  - Shows active race status
  - Validates horse racing system configuration
- **Usage:** `./scripts/dev_menu.sh` → Select option 8
- **Info:** Detailed horse racing diagnostics

#### `dev_menu.sh` Option 9 - Seed Horses Only
- **Purpose:** Adds only horse data to database
- **What it does:**
  - Seeds 24 diverse horses with realistic characteristics
  - Safe to run multiple times
- **Usage:** `./scripts/dev_menu.sh` → Select option 9
- **Quick:** Fast horse-only seeding

### 🔧 **Utility Scripts**

#### `dev_menu.sh` - Interactive Development Menu
- **Purpose:** Provides menu-driven access to all scripts
- **What it does:**
  - Shows all available operations (now includes horse racing options)
  - Guides you through choices
  - Handles errors gracefully
- **Usage:** `./scripts/dev_menu.sh`
- **User-friendly:** Perfect for beginners

## 🔄 Common Workflows

### Complete Reset for Testing
```bash
./scripts/teardown.sh     # Destroy everything
./scripts/fresh_start.sh  # Create fresh site with full data
```

### Quick Development Restart
```bash
./scripts/safe_restart.sh  # Restart containers, keep data
```

### Add Test Data to Empty Site
```bash
./scripts/seed_only.sh    # Add comprehensive test data (includes horses)
```

### Check Current Status
```bash
./scripts/quick_view.sh   # Quick database overview
```

### Horse Racing Specific Workflows
```bash
./scripts/dev_menu.sh     # Select option 8 for horse racing status
./scripts/dev_menu.sh     # Select option 9 to seed horses only
```

## 📊 What Gets Created by Fresh Start

### Users (12 total)
- **Admin Users:** `admin_casino`, `admin_sarah`
- **Regular Users:** `lucky_mike`, `gambler_jane`, `risk_taker_bob`, `slot_queen_amy`, `blackjack_tom`, `roulette_lisa`, `plinko_pete`, `horse_henry`, `mine_mary`, `newbie_nick`
- **Password:** `password123` for all users

### Financial Data
- **22 Wallets** across 3 currencies (USD, EUR, BTC)
- **142 Transactions** with realistic patterns
- **$4,800+ USD, €100M+ EUR, ₿0.6+ BTC** total money

### Gaming Data
- **6 Casino Games** (Enhanced Horse Racing, Blackjack, Roulette, Slots, Plinko, Minesweeper)
- **29 Game Rounds** with realistic timing
- **98 Bets** with proper win/loss ratios

### 🐎 Horse Racing System
- **24 Unique Horses** with diverse characteristics:
  - **Age Range:** 2-13 years (young speedsters to veteran horses)
  - **Speed Range:** 6.5-9.2 (creates competitive racing)
  - **Temperaments:** Confident, Aggressive, Nervous, Calm, Unpredictable
- **Dynamic Features:**
  - Physics-based race simulation
  - Odds calculation based on horse stats
  - Win/Place/Show betting options
  - Real-time race results with finishing times

### Sarcasm System
- **15 Sarcastic Templates** with 5 severity levels
- **12 User Settings** with personalized themes
- **6 UI Themes** (dark, light, casino, neon, classic, modern)

## 🛡️ Safety Features

### Confirmation Prompts
- All destructive operations ask for confirmation
- Clear warnings before data deletion
- Option to cancel at any time

### Data Protection
- `safe_restart.sh` preserves all data
- `seed_only.sh` won't duplicate existing data
- Database transactions ensure consistency

### Error Handling
- Scripts check container status
- Graceful failure with helpful messages
- Recovery suggestions provided

## 🎮 Testing the Site

After running any script that creates data:

1. **Visit:** http://localhost:8000
2. **Horse Racing:** http://localhost:8000/horse-racing
3. **Login:** Any username with password `password123`
4. **Admin Access:** Use `admin_casino` or `admin_sarah`
5. **Test Features:**
   - **🐎 Enhanced Horse Racing** with 24 real horses
   - Multi-currency wallets
   - Transaction history
   - Casino games
   - Sarcastic feedback
   - User settings

## 🐎 Horse Racing Testing Guide

### Start a New Race
1. Visit `/horse-racing`
2. Click "Start New Race"
3. View the 6 randomly selected horses with their stats and odds

### Place Bets
- Choose from Win, Place, or Show bets
- Odds are dynamically calculated based on horse characteristics
- Minimum bet: $1, Maximum bet: $1000

### Run the Race
- Physics-based simulation considers age, speed, and temperament
- View race results with finishing positions and times
- Automatic payout calculation based on original odds

## 🔍 Troubleshooting

### Containers Won't Start
```bash
docker-compose down -v  # Remove everything
./scripts/fresh_start.sh  # Start fresh
```

### Database Connection Issues
```bash
./scripts/quick_view.sh  # Check status
docker-compose logs db   # Check database logs
```

### Horse Racing Not Working
```bash
./scripts/dev_menu.sh    # Select option 8 to check horse racing status
./scripts/dev_menu.sh    # Select option 9 to seed horses if missing
```

### Want to Start Over Completely
```bash
./scripts/teardown.sh    # Nuclear option
./scripts/fresh_start.sh # Fresh start
```

## 💡 Tips

- Use `dev_menu.sh` for interactive guidance
- Run `quick_view.sh` to check status anytime
- `safe_restart.sh` is safe for code changes
- `fresh_start.sh` is perfect for demos
- Use option 8 in dev menu to check horse racing system
- `teardown.sh` only when you want to start completely fresh

All scripts are designed to be safe, user-friendly, and provide clear feedback about what they're doing! 