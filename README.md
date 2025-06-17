# Sarcastic Casino - Online Gambling Platform

A feature-rich online casino platform built with Flask, PostgreSQL, and Docker. The platform includes multiple games, user management, real-time analytics, and a sophisticated betting system.

## 🎮 Features

- Multiple casino games:
  - 🏇 Horse Racing with real-time odds
  - 🎰 Slots with animations
  - ♠️ Blackjack
  - 🎯 Plinko
- 📊 Real-time analytics dashboard
- 👥 User management system
- 💰 Virtual wallet and transaction tracking
- 🔒 Secure betting system

## 🚀 Quick Start with Docker

### Prerequisites

1. Install [Docker](https://docs.docker.com/get-docker/)
2. Install [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Project

1. Clone the repository:
```bash
git clone <repository-url>
cd Comp306-Project
```

2. Start the containers:
```bash
docker-compose up --build -d
```

3. Wait about 5 seconds for PostgreSQL to initialize, then seed the database:
```bash
docker-compose exec web bash scripts/seed.sh --clean --all
```

4. Access the site at http://localhost:8000

### Default Admin Login
- Username: `admin_casino`
- Password: `password123`

## 🎲 What Gets Seeded

The seeding process creates:
- 24 horses with unique stats and personalities
- 50 horse races with results
- 20 test users across 4 cohorts
- ~400 sample bets
- All game configurations
- Admin users

## 🛠 Development Commands

### Container Management
```bash
# Stop containers and remove volumes
docker-compose down -v

# Rebuild and start containers
docker-compose up --build -d

# View logs
docker-compose logs -f
```

### Database Management
```bash
# Reset and reseed database
docker-compose exec web bash scripts/seed.sh --clean --all

# Basic seed (games and admin only)
docker-compose exec web bash scripts/seed.sh --basic

# Add analytics data
docker-compose exec web bash scripts/seed.sh --analytics

# Add horse racing data only
docker-compose exec web bash scripts/seed.sh --horse-racing
```

## 📊 Database Structure

The platform uses PostgreSQL with the following main tables:
- `users`: User accounts and profiles
- `wallets`: Virtual wallets for each user
- `transactions`: All financial transactions
- `games`: Available casino games
- `rounds`: Game rounds/sessions
- `bets`: User bets and outcomes
- `horses`: Horse profiles and stats
- `horse_races`: Race events and results

## 🔧 Troubleshooting

1. If the site doesn't load after starting:
   - Wait a few more seconds for PostgreSQL to initialize
   - Check logs: `docker-compose logs -f`

2. If database seeding fails:
   - Stop containers: `docker-compose down -v`
   - Rebuild and start fresh: `docker-compose up --build -d`
   - Wait 5 seconds and try seeding again

3. If you need to reset everything:
   ```bash
   docker-compose down -v
   docker-compose up --build -d
   sleep 5
   docker-compose exec web bash scripts/seed.sh --clean --all
   ```

## 📝 License

This project is part of COMP 306 coursework.

## Quick Start (Docker - Automated Setup)

1. Setup scripts (after cloning):

```sh
# Option A: Run setup script
bash setup.sh

# Option B: Manual chmod
chmod +x scripts/*.sh
```

2. Build and run with full database seeding:

```sh
docker-compose up --build
```

3. Run the comprehensive setup script:

```sh
./scripts/fresh_start.sh
```

**Alternative:** Use interactive menu:
```sh
./scripts/dev_menu.sh
```

3. Visit [http://localhost:8000](http://localhost:8000) - Site is ready with test data!

**Login Credentials:**
- Any username with password: `password123`
- Admin users: `admin_casino` or `admin_sarah`

## Manual Setup (Docker)

## Manual Setup (Local Python)

1. Install requirements:

```sh
pip install -r requirements.txt
```

2. Set up Postgres and update `DATABASE_URL` in `.env`.
3. Initialize DB:

```sh
python init_db.py
python seed_games.py
```

4. Run the app:

```sh
flask run
```

---

- Python 3.12, Flask, SQLAlchemy, psycopg, pytest
- Postgres 16 (via Docker) 