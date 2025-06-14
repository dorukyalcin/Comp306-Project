# Table Query Scripts

This directory contains individual Python scripts that execute `SELECT * FROM table_name` queries for each database table in the horse racing application.

## Files

- `horses.py` - Query all horses (SELECT * FROM horses)
- `horse_runners.py` - Query all horse runners (SELECT * FROM horse_runners)
- `horse_results.py` - Query all horse results (SELECT * FROM horse_results)
- `rounds.py` - Query all rounds (SELECT * FROM rounds)
- `outcomes.py` - Query all outcomes (SELECT * FROM outcomes)
- `bets.py` - Query all bets (SELECT * FROM bets)
- `games.py` - Query all games (SELECT * FROM games)
- `run_all_queries.py` - Master script to run all queries at once

## Usage

### Run Individual Table Queries

To query a specific table, run the corresponding Python file:

```bash
python horses.py
python horse_runners.py
python horse_results.py
python rounds.py
python outcomes.py
python bets.py
python games.py
```

### Run All Table Queries

To run all table queries at once:

```bash
python run_all_queries.py
```

## Requirements

- These scripts require the Flask application context to be available
- Make sure `app.py` and `models.py` are in the parent directory
- The database connection must be properly configured in your Flask app

## Output

Each script will:
1. Connect to the database using the Flask app context
2. Execute the equivalent of `SELECT * FROM table_name`
3. Display all records in a readable format
4. Show the total count of records found

The output includes all fields for each record, making it easy to inspect the complete database contents for each table. 