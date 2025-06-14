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
  - Adds comprehensive test data (12 users, transactions, bets, sarcasm system)
- **Usage:** `./scripts/fresh_start.sh`
- **Result:** Full testing environment with ~400 database records

#### `safe_restart.sh` - Safe Container Restart
- **Purpose:** Restarts containers while preserving all database data
- **What it does:**
  - Stops containers gracefully
  - Rebuilds and restarts containers
  - Preserves all user data, transactions, etc.
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
  - Runs comprehensive seeding script
  - Skips if users already exist
- **Usage:** `./scripts/seed_only.sh`
- **Safe:** Won't duplicate data

#### `quick_view.sh` - Quick Status Check
- **Purpose:** Shows current database status and site health
- **What it does:**
  - Shows container status
  - Displays database record counts
  - Shows sample users and total money
- **Usage:** `./scripts/quick_view.sh`
- **Fast:** Quick overview without detailed data

### 🔧 **Utility Scripts**

#### `dev_menu.sh` - Interactive Development Menu
- **Purpose:** Provides menu-driven access to all scripts
- **What it does:**
  - Shows all available operations
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
./scripts/seed_only.sh    # Add comprehensive test data
```

### Check Current Status
```bash
./scripts/quick_view.sh   # Quick database overview
```

## 📊 What Gets Created by Fresh Start

### Users (12 total)
- **Admin Users:** `admin_casino`, `admin_sarah`
- **Regular Users:** `lucky_mike`, `gambler_jane`, `risk_taker_bob`, `slot_queen_amy`, `blackjack_tom`, `roulette_lisa`, `plinko_pete`, `horse_henry`, `mine_mary`, `newbie_nick`
- **Password:** `password123` for all users

### Financial Data
- **26 Wallets** across 3 currencies (USD, EUR, BTC)
- **143 Transactions** with realistic patterns
- **$4,000+ USD, €3,000+ EUR, ₿3+ BTC** total money

### Gaming Data
- **6 Casino Games** (Horse Racing, Blackjack, Roulette, Slots, Plinko, Minesweeper)
- **25 Game Rounds** with realistic timing
- **98 Bets** with proper win/loss ratios

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
2. **Login:** Any username with password `password123`
3. **Admin Access:** Use `admin_casino` or `admin_sarah`
4. **Test Features:**
   - Multi-currency wallets
   - Transaction history
   - Casino games
   - Sarcastic feedback
   - User settings

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
- `teardown.sh` only when you want to start completely fresh

All scripts are designed to be safe, user-friendly, and provide clear feedback about what they're doing! 