# Sarcastic Gambling Site

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