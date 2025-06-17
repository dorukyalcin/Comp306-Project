from app import app, db
from models import Horse, HorseResult, HorseRunner, Round, Game, Bet
from sqlalchemy import text

with app.app_context():
    print("\n=== Database Table Counts ===")
    print(f"Horses: {Horse.query.count()}")
    print(f"Horse Results: {HorseResult.query.count()}")
    print(f"Horse Runners: {HorseRunner.query.count()}")
    
    print("\n=== Sample Horse Data ===")
    horse = Horse.query.first()
    if horse:
        print(f"Horse: {horse.name} (ID: {horse.horse_id})")
        print(f"Age: {horse.age}")
        print(f"Base Speed: {horse.base_speed}")
        print(f"Temperament: {horse.temperament}")
    else:
        print("No horses found!")
        
    print("\n=== Sample Result Data ===")
    result = HorseResult.query.first()
    if result:
        print(f"Round ID: {result.round_id}")
        print(f"Horse ID: {result.horse_id}")
        print(f"Lane: {result.lane_no}")
        print(f"Finish Place: {result.finish_place}")
        print(f"Race Time: {result.race_time_sec}")
    else:
        print("No results found!")
        
    print("\n=== Direct SQL Query Test ===")
    test_query = """
    SELECT 
        h.horse_id,
        h.name,
        COUNT(hr.round_id) as races_run,
        COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) as wins,
        COUNT(CASE WHEN hr.finish_place <= 3 THEN 1 END) as top3,
        AVG(hr.finish_place) as avg_place,
        MIN(hr.race_time_sec) as best_time
    FROM horses h
    LEFT JOIN horse_results hr ON h.horse_id = hr.horse_id
    GROUP BY h.horse_id, h.name
    ORDER BY COUNT(CASE WHEN hr.finish_place = 1 THEN 1 END) DESC
    LIMIT 5;
    """
    
    try:
        result = db.session.execute(text(test_query))
        rows = result.fetchall()
        print("\nTest query results:")
        for row in rows:
            print(f"Horse: {row.name}")
            print(f"  Races: {row.races_run}")
            print(f"  Wins: {row.wins}")
            print(f"  Top 3: {row.top3}")
            print(f"  Avg Place: {row.avg_place:.2f}")
            print(f"  Best Time: {row.best_time:.2f}s")
            print()
    except Exception as e:
        print("Query error:", str(e))
        
    print("\n=== Game Check ===")
    horse_game = Game.query.filter_by(code='HORSE').first()
    if horse_game:
        print(f"Horse Racing Game ID: {horse_game.game_id}")
        rounds = Round.query.filter_by(game_id=horse_game.game_id).count()
        print(f"Total Horse Racing Rounds: {rounds}")
        
        # Check a specific round's results
        sample_round = Round.query.filter_by(game_id=horse_game.game_id).first()
        if sample_round:
            print(f"\nSample Round {sample_round.round_id}:")
            results = HorseResult.query.filter_by(round_id=sample_round.round_id).all()
            for result in results:
                print(f"  Horse {result.horse_id}: Place {result.finish_place}, Time {result.race_time_sec}s")
    else:
        print("Horse Racing game not found!") 