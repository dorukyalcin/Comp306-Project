# Sarcastic Gambling Site

## Setup (Docker)

1. Copy `.env.example` to `.env` and adjust if needed.
2. Build and run:

```sh
docker-compose up --build
```

3. Initialize the database (in another terminal):

```sh
docker-compose run web python init_db.py
```

4. Seed the games table:

```sh
docker-compose run web python seed_games.py
```

5. Visit [http://localhost:8000/health](http://localhost:8000/health) to check the app is running.

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