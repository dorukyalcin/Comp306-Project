# Database Seeding

This directory contains all database seeding scripts and related documentation for the Sarcastic Gambling Site.

## 📁 Python Seeding Scripts

### 🌱 **Core Seeding Scripts**

#### `comprehensive_seed.py` - Complete Test Data
- **Purpose:** Creates comprehensive test data for all database entities
- **What it creates:**
  - 12 Users (2 admins, 10 regular users)
  - 26 Multi-currency wallets (USD, EUR, BTC)
  - 143 Realistic transactions
  - 25 Game rounds with betting history
  - 98 Bets with proper win/loss ratios
  - 15 Sarcastic templates (5 severity levels)
  - 12 User settings with themes
- **Usage:** `python seeding/comprehensive_seed.py`
- **Safe:** Won't duplicate if users already exist

#### `seed_games.py` - Games Catalog
- **Purpose:** Populates the games table with casino games
- **What it creates:**
  - 6 Casino games (Horse Racing, Blackjack, Roulette, Slots, Plinko, Minesweeper)
  - Game-specific rules and payout configurations
  - Min/max bet limits and house edge settings
- **Usage:** `python seeding/seed_games.py`
- **Required:** Must run before comprehensive seeding

#### `startup_with_seed.py` - Complete Initialization
- **Purpose:** Full database initialization with all data
- **What it does:**
  - Waits for database connection
  - Creates all tables
  - Seeds games catalog
  - Runs comprehensive seeding
  - Provides status summary
- **Usage:** `python seeding/startup_with_seed.py`
- **Best for:** Fresh start with everything

### 🔧 **Database Management Scripts**

#### `init_db.py` - Table Creation
- **Purpose:** Creates all database tables
- **What it does:**
  - Runs `db.create_all()`
  - Safe to run multiple times
  - Only creates missing tables
- **Usage:** `python seeding/init_db.py`
- **Safe:** No data deletion

#### `reset_db.py` - Database Reset
- **Purpose:** Completely resets the database
- **What it does:**
  - Drops all tables (`db.drop_all()`)
  - Recreates all tables (`db.create_all()`)
  - **DELETES ALL DATA**
- **Usage:** `python seeding/reset_db.py`
- **⚠️ WARNING:** Destructive operation

#### `view_db.py` - Database Inspection
- **Purpose:** Shows detailed database contents
- **What it displays:**
  - All table names
  - Record counts for each entity
  - Sample data from each table
  - Total money in system
  - Comprehensive database summary
- **Usage:** `python seeding/view_db.py`
- **Safe:** Read-only operation

## 📊 Data Relationships

### Entity Dependencies (Seeding Order)
1. **SarcasTemp** → Templates for user settings
2. **Users** → Core user accounts
3. **Wallets** → User financial accounts
4. **Transactions** → Financial history
5. **Games** → Casino game catalog
6. **Rounds** → Game sessions
7. **Outcomes** → Game results
8. **Bets** → User gambling activity
9. **UserSettings** → User preferences

### Foreign Key Relationships
- `UserSettings.user_id` → `Users.user_id`
- `UserSettings.sarcas_template_id` → `SarcasTemp.template_id`
- `Wallets.user_id` → `Users.user_id`
- `Transactions.wallet_id` → `Wallets.wallet_id`
- `Rounds.game_id` → `Games.game_id`
- `Outcomes.round_id` → `Rounds.round_id`
- `Bets.user_id` → `Users.user_id`
- `Bets.round_id` → `Rounds.round_id`
- `Bets.outcome_id` → `Outcomes.outcome_id`

## 🎮 Game Data Specifications

### Game Types and JSON Schemas

#### Horse Racing (`HORSE`)
```json
{
  "choice_data": {"bet_type": "win", "horse": 4},
  "outcome_data": {"order": [4,2,6,1,3,5]},
  "payout_rule_json": {"type": "pari-mutuel", "runners": 6}
}
```

#### Blackjack (`BJ21`)
```json
{
  "choice_data": {"actions": ["H","S"], "hand": [10,6]},
  "outcome_data": {"dealer": [10,"A"], "result": "win"},
  "payout_rule_json": {"dealer_stands_on": 17, "blackjack_pays": "3:2"}
}
```

#### Roulette (`ROULETTE`)
```json
{
  "choice_data": {"bet_type": "straight", "number": 17},
  "outcome_data": {"number": 22},
  "payout_rule_json": {"wheel": "single-zero"}
}
```

#### Slot Machine (`SLOT`)
```json
{
  "choice_data": {"lines": [1,2,3]},
  "outcome_data": {"reel_stop": [4,3,7,3,4], "payout": 25},
  "payout_rule_json": {"reels": 5, "paylines": 20, "rtp": 96}
}
```

#### Plinko (`PLINKO`)
```json
{
  "choice_data": {},
  "outcome_data": {"bin": 3, "multiplier": 2},
  "payout_rule_json": {"rows": 16, "multipliers": [0.5,1,2,5,10]}
}
```

#### Minesweeper (`MINESWEEP`)
```json
{
  "choice_data": {"squares_revealed": 7},
  "outcome_data": {"mine_hit": false},
  "payout_rule_json": {"grid": "5x5", "mines": 1, "no_hints": true}
}
```

## 💰 Financial Data Patterns

### Currency Distribution
- **USD:** $500-$3,000 starting balances
- **EUR:** €400-€2,400 starting balances  
- **BTC:** ₿0.1-₿1.5 starting balances

### Transaction Types
- `deposit` - Money added to account
- `withdraw` - Money removed from account
- `bet_win` - Winnings from successful bets
- `bet_loss` - Losses from unsuccessful bets

### Realistic Patterns
- 3-8 transactions per wallet
- Varied transaction amounts per currency
- Proper balance calculations
- Timestamp distribution over 60 days

## 😏 Sarcasm System Details

### Template Severity Levels
1. **Level 1 (Mild):** Light teasing
2. **Level 2 (Light):** Gentle mockery
3. **Level 3 (Medium):** Noticeable sarcasm
4. **Level 4 (Strong):** Heavy sarcasm
5. **Level 5 (Maximum):** Brutal honesty

### User Preferences
- **Sarcasm Tolerance:** 1-5 (matches template severity)
- **UI Themes:** dark, light, casino, neon, classic, modern
- **Template Matching:** Users get templates ≤ their tolerance level

## 🔄 Common Usage Patterns

### Fresh Database Setup
```bash
python seeding/init_db.py           # Create tables
python seeding/seed_games.py        # Add games
python seeding/comprehensive_seed.py # Add all test data
```

### Complete Reset
```bash
python seeding/reset_db.py          # Wipe everything
python seeding/startup_with_seed.py # Fresh start
```

### Data Inspection
```bash
python seeding/view_db.py           # Detailed view
```

## 🛡️ Safety Features

### Data Protection
- Comprehensive seeding checks for existing users
- Transactions maintain referential integrity
- Proper decimal handling for financial data
- Timestamp consistency across related records

### Error Handling
- Database connection validation
- Graceful failure with helpful messages
- Transaction rollback on errors
- Foreign key constraint enforcement

## 📈 Expected Results

After running comprehensive seeding:
- **Total Records:** ~400 database entries
- **User Accounts:** 12 fully configured users
- **Financial Volume:** $10,000+ equivalent across currencies
- **Gaming Activity:** Realistic betting patterns and history
- **System Features:** Complete sarcasm and settings system

All scripts are designed to work together seamlessly and provide a realistic testing environment for the sarcastic gambling site. 