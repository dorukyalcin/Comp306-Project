Sarcastic Gambling Site – Consolidated Design Document (Refreshed)
1  Project Overview & Functional Requirements
This document consolidates the entire design of the sarcastic gambling site for your DBMS course. It includes ER diagrams (in Mermaid), relational schema, games catalogue, JSON contracts, seed SQL, development sprint plan, and environment setup. All layers are 100 % Python on top of PostgreSQL.
2  ER Diagrams
2.1  Conceptual (Chen) – Mermaid source

```mermaid
erDiagram
    USER ||--o{ WALLET : has
    USER ||--o{ BET : places
    USER ||--|| USER_SETTINGS : "customises"
    
    WALLET ||--o{ TRANSACTION : logs
    BET }o--|| ROUND : "belongs to"
    ROUND }o--|| GAME : "instance of"
    ROUND ||--|| OUTCOME : "produces"
    
    SARCASTEMPS ||--o{ USER_SETTINGS : "uses level from"
```

2.2  Logical (Crow‑foot) – Mermaid source

```mermaid
erDiagram
    USERS {
        int PK user_id
        varchar username
        varchar email
        char(128) pw_hash
        bool  is_admin
        timestamptz created_at
    }
    USER_SETTINGS {
        int PK FK user_id
        smallint sarcasm_level
        text    theme
    }

    WALLETS {
        int PK wallet_id
        int FK user_id
        varchar currency
        numeric balance
    }
    TRANSACTIONS {
        bigint PK txn_id
        int FK wallet_id
        numeric amount
        varchar txn_type
        timestamptz created_at
    }

    GAMES {
        int PK game_id
        varchar code
        numeric house_edge
        numeric min_bet
        numeric max_bet
        bool is_active
    }
    ROUNDS {
        bigint PK round_id
        int FK game_id
        timestamptz started_at
        timestamptz ended_at
        varchar rng_seed
    }
    OUTCOMES {
        bigint PK outcome_id
        bigint FK round_id
        json   outcome_data
        numeric payout_multiplier
    }
    BETS {
        bigint PK bet_id
        bigint FK round_id
        int FK user_id
        numeric amount
        json   choice_data
        timestamptz placed_at
        timestamptz settled_at
        bigint FK outcome_id
        numeric payout_amount
    }

    SARCASTEMPS {
        int PK template_id
        text template_text
        smallint severity_level
    }

    USERS ||--o{ WALLETS : owns
    WALLETS ||--o{ TRANSACTIONS : "records"
    USERS ||--o{ BETS : places
    USER_SETTINGS ||--|| USERS : "1‑to‑1"
    ROUNDS ||--o{ BETS : "aggregates"
    GAMES ||--o{ ROUNDS : instantiates
    ROUNDS ||--|| OUTCOMES : "yields"
    SARCASTEMPS ||--o{ USER_SETTINGS : "level ref"
```

3  Games Catalogue
game_id	code	title	house_edge	min_bet	max_bet	notes / payout_rule_json
1	HORSE	At Yarışı (Horse Racing)	6 %	1	1000	{"type":"pari‑mutuel","runners":6}
2	BJ21	Blackjack 21	1.5 %	1	500	{"dealer_stands_on":17,"blackjack_pays":"3:2"}
3	ROULETTE	Roulette (European)	2.7 %	1	1000	{"wheel":"single‑zero"}
4	SLOT	Sarcasm Slots	4 %	0.20	50	{"reels":5,"paylines":20,"rtp":96}
5	PLINKO	Plinko	3 %	0.10	200	{"rows":16,"multipliers":[0.5,1,2,5,10]}
6	MINESWEEP	Mine Sweeper (1 mine)	5 %	0.10	200	{"grid":"5x5","mines":1,"no_hints":true}
4  JSON Mini‑Schemas
Game	choice_data	outcome_data	Payout note
Horse (HORSE)	{"bet_type":"win","horse":4}	{"order":[4,2,6,1,3,5]}	position compare
Blackjack (BJ21)	{"actions":["H","S"],"hand":[10,6]}	{"dealer":[10,"A"],"result":"lose"}	result→multiplier
Roulette (ROULETTE)	{"bet_type":"straight","number":17}	{"number":22}	table mapping
Slot (SLOT)	{"lines":[1,2,3]}	{"reel_stop":[4,3,7,3,4],"payout":25}	payout included
Plinko (PLINKO)	{}	{"bin":3,"multiplier":2}	stake×multiplier
Mine Sweeper (MINESWEEP)	{"squares_revealed":7}	{"mine_hit":false}	mine_hit loses
5  Seed SQL for games

```sql
INSERT INTO games (code, house_edge, min_bet, max_bet, is_active, payout_rule_json)
VALUES
  ('HORSE',    0.06, 1.00 , 1000.00, TRUE,
   '{"type":"pari-mutuel","runners":6}'),
  ('BJ21',     0.015,1.00 , 500.00 , TRUE,
   '{"dealer_stands_on":17,"blackjack_pays":"3:2"}'),
  ('ROULETTE', 0.027,1.00 , 1000.00, TRUE,
   '{"wheel":"single-zero"}'),
  ('SLOT',     0.04 ,0.20 , 50.00  , TRUE,
   '{"reels":5,"paylines":20,"rtp":96}'),
  ('PLINKO',   0.03 ,0.10 , 200.00 , TRUE,
   '{"rows":16,"multipliers":[0.5,1,2,5,10]}'),
  ('MINESWEEP',0.05 ,0.10 , 200.00 , TRUE,
   '{"grid":"5x5","mines":1,"no_hints":true}');
```

6  Settlement Trigger / Function Checklist
- HORSE: finish_race(round_id) stored proc loops through unsettled bets.
- BJ21: bj_play() Python helper simulates dealer, returns outcome JSON.
- ROULETTE: spin_wheel() stored proc returns 0–36.
- SLOT / PLINKO / MINESWEEP: Python RNG functions produce outcome JSON.
All call credit_wallet(user_id, payout_amount, bet_id).
7  17‑Day Sprint Plan & Environment Setup
See sections in previous version; unchanged except games catalogue added on Day 3.
Environment: Python 3.12, Flask, SQLAlchemy, psycopg[binary], pytest.
Docker Compose services: db (Postgres 16) & web (Gunicorn).

