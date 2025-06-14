# 🎮 Games Package

This directory contains all game implementations for the Sarcastic Casino application. Each game is implemented as a separate class following standardized patterns.

## 📁 Directory Structure

```
games/
├── __init__.py           # Package initialization and game registry
├── README.md            # This file
├── horse_racing.py      # Horse racing game implementation
└── [future_games].py    # Future game implementations
```

## 🏗️ Game Implementation Pattern

Each game class should follow this standardized pattern:

### **Required Methods**
```python
class GameName:
    def __init__(self):
        self.game_code = 'GAME_CODE'  # Database identifier
        # Game-specific configuration
    
    def get_game(self):
        """Get game from database"""
        
    def validate_game_setup(self):
        """Validate game configuration"""
        
    def get_active_round(self):
        """Get currently active game round"""
        
    def start_new_round(self):
        """Start a new game round"""
        
    def place_bet(self, user_id, bet_data, bet_amount):
        """Place a bet in the game"""
        
    def execute_game(self):
        """Execute the game and determine outcome"""
        
    def get_game_status(self, user_id=None):
        """Get current game status"""
```

### **Standardized Return Format**
All methods should return dictionaries with consistent structure:

```python
# Success response
{
    'success': True,
    'data': {...},
    'message': 'Operation completed successfully'
}

# Error response
{
    'success': False,
    'message': 'Error description',
    'error_code': 'ERROR_TYPE'  # Optional
}
```

## 🎯 Available Games

### 🐎 **Horse Racing** (`horse_racing.py`)
- **Code**: `HORSE`
- **Class**: `HorseRacing`
- **Features**: 6-horse races, win betting, 2.5x payout
- **Status**: ✅ Implemented

### 🃏 **Future Games**

#### **Blackjack** (`blackjack.py`) - Planned
- **Code**: `BJ21`
- **Class**: `Blackjack`
- **Features**: Standard blackjack rules, dealer AI

#### **Roulette** (`roulette.py`) - Planned
- **Code**: `ROULETTE`
- **Class**: `Roulette`
- **Features**: European roulette, multiple bet types

#### **Slot Machine** (`slots.py`) - Planned
- **Code**: `SLOT`
- **Class**: `Slots`
- **Features**: 5-reel slots, multiple paylines

#### **Plinko** (`plinko.py`) - Planned
- **Code**: `PLINKO`
- **Class**: `Plinko`
- **Features**: 16-row Plinko board, multiplier payouts

#### **Minesweeper** (`minesweeper.py`) - Planned
- **Code**: `MINESWEEP`
- **Class**: `Minesweeper`
- **Features**: 5x5 grid, single mine, progressive payouts

## 📝 Adding a New Game

### 1. **Create Game File**
```bash
touch games/new_game.py
```

### 2. **Implement Game Class**
```python
# games/new_game.py
from models import db, Game, Round, Bet, Outcome
from decimal import Decimal

class NewGame:
    def __init__(self):
        self.game_code = 'NEW_GAME'
        # Game configuration
    
    # Implement required methods...
```

### 3. **Register in Package**
```python
# games/__init__.py
from .new_game import NewGame

AVAILABLE_GAMES = {
    'HORSE': HorseRacing,
    'NEW_GAME': NewGame,  # Add here
}
```

### 4. **Add Flask Routes**
```python
# app.py
from games import NewGame

@app.route('/new-game')
@login_required
def new_game():
    ng = NewGame()
    # Implementation...
```

### 5. **Create Frontend Template**
```html
<!-- templates/new_game.html -->
{% extends "base.html" %}
{% block content %}
<!-- Game UI -->
{% endblock %}
```

## 🔧 Game Registry Usage

The games package provides utility functions for dynamic game loading:

```python
from games import get_game_class, create_game_instance, get_available_games

# Get all available games
games = get_available_games()  # ['HORSE']

# Get specific game class
HorseRacing = get_game_class('HORSE')

# Create game instance
hr = create_game_instance('HORSE')
```

## 🧪 Testing Games

Each game should include comprehensive tests:

```python
# tests/test_horse_racing.py
import unittest
from games import HorseRacing

class TestHorseRacing(unittest.TestCase):
    def setUp(self):
        self.hr = HorseRacing()
    
    def test_game_validation(self):
        result = self.hr.validate_game_setup()
        self.assertTrue(result['valid'])
    
    # More tests...
```

## 🎨 Frontend Integration

### **Game Cards on Homepage**
```html
<!-- templates/index.html -->
{% for game_code in available_games %}
    <div class="game-card">
        <h5>{{ game_names[game_code] }}</h5>
        <a href="{{ url_for(game_code.lower() + '_game') }}">Play Now</a>
    </div>
{% endfor %}
```

### **Dynamic Game Loading**
```python
# app.py
@app.context_processor
def inject_games():
    from games import get_available_games
    return {
        'available_games': get_available_games(),
        'game_names': {
            'HORSE': 'Horse Racing',
            'BJ21': 'Blackjack',
            # ...
        }
    }
```

## 🏆 Best Practices

1. **Consistent Error Handling**: Use try/catch blocks with database rollback
2. **Input Validation**: Validate all user inputs before processing
3. **Decimal Precision**: Use `Decimal` for all monetary calculations
4. **Transaction Safety**: Ensure database consistency
5. **Documentation**: Document all public methods
6. **Testing**: Write unit tests for all game logic
7. **Security**: Validate user permissions and game state

## 📊 Game Performance Metrics

Track these metrics for each game:
- Active players
- Total bets placed
- House edge performance
- Average session duration
- Player retention rates

This structure provides a scalable foundation for adding multiple casino games while maintaining code quality and consistency! 