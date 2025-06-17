from app import app, db
from models import Horse, HorseResult, HorseRunner, Bet
from sqlalchemy import text

with app.app_context():
    print("=== Debug Horse Racing Query ===")
    
    # Step 1: Check basic horse data
    print("\n1. Basic Horse Data:")
    horses = Horse.query.all()
    print(f"Total horses: {len(horses)}")
    if horses:
        print("Sample horse:", horses[0].name, "ID:", horses[0].horse_id)
    
    # Step 2: Check race results
    print("\n2. Race Results:")
    results = HorseResult.query.all()
    print(f"Total results: {len(results)}")
    if results:
        print("Sample result - Horse ID:", results[0].horse_id, "Place:", results[0].finish_place)
    
    # Step 3: Check horse runners
    print("\n3. Horse Runners:")
    runners = HorseRunner.query.all()
    print(f"Total runners: {len(runners)}")
    if runners:
        print("Sample runner - Horse ID:", runners[0].horse_id, "Odds:", runners[0].odds)
    
    # Step 4: Check horse-related bets
    print("\n4. Horse Racing Bets:")
    horse_bets = Bet.query.filter(Bet.choice_data.isnot(None)).all()
    print(f"Total bets with choice data: {len(horse_bets)}")
    if horse_bets:
        print("Sample bet:", horse_bets[0].choice_data)
    
    # Step 5: Try the full query
    print("\n5. Testing Full Query:")
    query = """
    WITH horse_race_stats AS (
        SELECT 
            h.horse_id,
            h.name,
            COUNT(hr.round_id) as races_run,
            COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) as wins
        FROM horses h
        LEFT JOIN horse_results hr ON h.horse_id = hr.horse_id
        GROUP BY h.horse_id, h.name
        HAVING COUNT(hr.round_id) > 0
    )
    SELECT name, races_run, wins
    FROM horse_race_stats
    LIMIT 5;
    """
    
    try:
        result = db.session.execute(text(query))
        rows = result.fetchall()
        print("\nQuery results:")
        for row in rows:
            print(f"Horse: {row.name}, Races: {row.races_run}, Wins: {row.wins}")
    except Exception as e:
        print("Query error:", str(e)) 