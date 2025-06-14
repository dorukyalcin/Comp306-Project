# 🐎 HorseRacing Class Documentation

## Overview

The `HorseRacing` class is a dedicated handler for all horse racing game functionality in the Sarcastic Casino application. This class follows the **separation of concerns** principle by encapsulating all horse racing logic in a single, reusable class.

## 📁 File Structure

```
project/
├── games/
│   ├── __init__.py       # Games package initialization
│   ├── README.md         # Games package documentation
│   └── horse_racing.py   # HorseRacing class definition
├── app.py               # Flask routes (refactored to use HorseRacing class)
├── models.py            # Database models
└── templates/
    └── horse_racing.html # Frontend template
```

## 🏗️ Class Architecture

### Class Properties

```python
class HorseRacing:
    def __init__(self):
        self.game_code = 'HORSE'        # Game identifier in database
        self.num_horses = 6             # Number of horses in race
        self.horse_names = {            # Horse names mapping
            1: "Lightning Bolt",
            2: "Thunder Strike", 
            3: "Wind Runner",
            4: "Fire Dash",
            5: "Storm Chaser",
            6: "Star Galloper"
        }
```

## 🔧 Core Methods

### 1. **Game Management**

#### `get_game()`
- **Purpose**: Retrieve horse racing game from database
- **Returns**: `Game` object or `None`
- **Usage**: Internal method for game validation

#### `validate_game_setup()`
- **Purpose**: Validate game configuration and availability
- **Returns**: Dict with validation status and game info
- **Example**:
```python
hr = HorseRacing()
validation = hr.validate_game_setup()
if validation['valid']:
    # Game is ready
    game_info = validation['game_info']
```

### 2. **Race Management**

#### `start_new_race()`
- **Purpose**: Create a new race round
- **Returns**: Dict with success status and round_id
- **Features**:
  - Checks for existing active races
  - Generates unique RNG seed
  - Database transaction handling

#### `get_active_round()`
- **Purpose**: Get currently active race round
- **Returns**: `Round` object or `None`
- **Usage**: Check if race is in progress

#### `get_recent_rounds(limit=10)`
- **Purpose**: Get recent completed races
- **Parameters**: `limit` - Number of races to retrieve
- **Returns**: List of `Round` objects

### 3. **Betting System**

#### `place_bet(user_id, horse_number, bet_amount, bet_type='win')`
- **Purpose**: Place a bet on a horse
- **Parameters**:
  - `user_id` (int): User placing the bet
  - `horse_number` (int): Horse selection (1-6)
  - `bet_amount` (Decimal): Amount to bet
  - `bet_type` (str): Type of bet ('win', 'place', 'show')
- **Returns**: Dict with success status and message
- **Features**:
  - Input validation
  - Balance checking
  - Duplicate bet prevention
  - Transaction creation

#### `get_betting_stats(round_id=None)`
- **Purpose**: Get betting statistics for a race
- **Parameters**: `round_id` - Specific round (defaults to active)
- **Returns**: Dict with betting statistics
- **Example**:
```python
hr = HorseRacing()
stats = hr.get_betting_stats()
print(f"Total bets: {stats['total_bets']}")
print(f"Total amount: ${stats['total_amount']}")
```

### 4. **Race Execution**

#### `run_race()`
- **Purpose**: Execute race and determine winner
- **Returns**: Dict with race results
- **Features**:
  - Random race outcome generation
  - Payout calculation (2.5x for winners)
  - Winner list with payout details
  - Database transaction handling

#### `get_race_status(user_id=None)`
- **Purpose**: Get current race status
- **Parameters**: `user_id` - Optional user for personal bet info
- **Returns**: Dict with race status
- **Features**:
  - Active race detection
  - Bet count tracking
  - User-specific bet information

### 5. **Information & Utilities**

#### `get_horse_info()`
- **Purpose**: Get horse information and metadata
- **Returns**: Dict with horse details
- **Example**:
```python
hr = HorseRacing()
info = hr.get_horse_info()
for horse in info['horses']:
    print(f"{horse['emoji']} Horse #{horse['number']}: {horse['name']}")
```

## 🎯 Usage Examples

### Basic Usage in Flask Routes

```python
from games import HorseRacing

@app.route('/horse-racing')
@login_required
def horse_racing():
    hr = HorseRacing()
    
    # Validate game setup
    validation = hr.validate_game_setup()
    if not validation['valid']:
        flash(validation['message'], 'danger')
        return redirect(url_for('index'))
    
    # Get game data
    game = hr.get_game()
    active_round = hr.get_active_round()
    recent_rounds = hr.get_recent_rounds()
    
    return render_template('horse_racing.html',
                         game=game,
                         active_round=active_round,
                         recent_rounds=recent_rounds)

@app.route('/horse-racing/place-bet', methods=['POST'])
@login_required
def place_horse_bet():
    data = request.get_json()
    hr = HorseRacing()
    
    result = hr.place_bet(
        user_id=current_user.user_id,
        horse_number=data.get('horse'),
        bet_amount=Decimal(str(data.get('amount'))),
        bet_type=data.get('bet_type', 'win')
    )
    
    return jsonify(result)
```

### Advanced Usage with Error Handling

```python
def handle_race_workflow():
    hr = HorseRacing()
    
    try:
        # Start race
        race_result = hr.start_new_race()
        if not race_result['success']:
            return {'error': race_result['message']}
        
        round_id = race_result['round_id']
        
        # Get betting stats
        stats = hr.get_betting_stats(round_id)
        
        # Run race when ready
        if stats['total_bets'] > 0:
            race_result = hr.run_race()
            return race_result
        
        return {'status': 'waiting_for_bets'}
        
    except Exception as e:
        return {'error': f'Race workflow error: {str(e)}'}
```

## 🏆 Benefits of This Architecture

### **1. Separation of Concerns**
- **Routes**: Handle HTTP requests/responses only
- **HorseRacing Class**: Handle all game logic
- **Models**: Handle data persistence

### **2. Reusability**
- Class can be used in multiple contexts
- Easy to test independently
- Potential for future game variations

### **3. Maintainability**
- All horse racing logic in one place
- Clear method responsibilities
- Easy to extend with new features

### **4. Error Handling**
- Centralized error management
- Database transaction safety
- Consistent error responses

### **5. Testing**
- Easy to unit test individual methods
- Mock database interactions
- Test game logic separately from routes

## 🚀 Future Enhancements

The class structure allows for easy extension:

1. **Multiple Bet Types**: Add 'place' and 'show' betting
2. **Dynamic Odds**: Calculate odds based on betting pools
3. **Horse Statistics**: Track win/loss records
4. **Race Commentary**: Generate race descriptions
5. **Tournament Mode**: Multi-race tournaments

## 📊 API Endpoints Using the Class

| Endpoint | Method | HorseRacing Method | Purpose |
|----------|--------|-------------------|---------|
| `/horse-racing` | GET | `get_game()`, `get_active_round()` | Main game page |
| `/horse-racing/start-race` | POST | `start_new_race()` | Start new race |
| `/horse-racing/place-bet` | POST | `place_bet()` | Place bet |
| `/horse-racing/run-race` | POST | `run_race()` | Execute race |
| `/horse-racing/race-status` | GET | `get_race_status()` | Get race status |
| `/horse-racing/betting-stats` | GET | `get_betting_stats()` | Get betting statistics |
| `/horse-racing/horse-info` | GET | `get_horse_info()` | Get horse information |

## 🔒 Security Features

- **Input Validation**: All inputs validated before processing
- **Balance Checking**: Prevents betting more than available funds
- **Duplicate Prevention**: One bet per user per race
- **Transaction Safety**: Database rollback on errors
- **Authentication**: All methods assume authenticated users

## 💡 Best Practices

1. **Always instantiate a new HorseRacing object** for each request
2. **Check validation results** before proceeding with operations
3. **Handle error responses** appropriately in your UI
4. **Use proper Decimal types** for monetary calculations
5. **Test with various edge cases** (no funds, no active race, etc.)

This architecture provides a solid foundation for the horse racing game while maintaining clean, maintainable, and extensible code! 