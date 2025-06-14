"""
Games Package for Sarcastic Casino

This package contains all game implementations for the casino application.
Each game is implemented as a separate class with standardized methods.

Available Games:
- HorseRacing: Horse racing game with betting and race simulation
- Slots: Classic 3-reel slot machine with standard symbols

Usage:
    from games.horse_racing import HorseRacing
    from games.slots import Slots
    from games import HorseRacing, Slots  # Alternative import

Future Games:
- Blackjack
- Roulette
- Plinko
- Minesweeper
"""

from .horse_racing import HorseRacing
from .slots import Slots
from .plinko import Plinko
from .blackjack import Blackjack

# Export all available games
__all__ = ['HorseRacing', 'Slots', 'Plinko', 'Blackjack']

# Game registry for dynamic loading
AVAILABLE_GAMES = {
    'HORSE': HorseRacing,
    'SLOT': Slots,
    'PLINKO': Plinko,
    'BJ21': Blackjack,
    # Future games will be added here
    # 'ROULETTE': Roulette,
    # 'MINESWEEP': Minesweeper,
}

def get_game_class(game_code):
    """
    Get a game class by its code
    
    Args:
        game_code (str): The game code (e.g., 'HORSE', 'SLOT')
        
    Returns:
        Game class or None if not found
    """
    return AVAILABLE_GAMES.get(game_code)

def get_available_games():
    """
    Get list of all available game codes
    
    Returns:
        list: List of available game codes
    """
    return list(AVAILABLE_GAMES.keys())

def create_game_instance(game_code):
    """
    Create an instance of a game by its code
    
    Args:
        game_code (str): The game code
        
    Returns:
        Game instance or None if game not found
    """
    game_class = get_game_class(game_code)
    if game_class:
        return game_class()
    return None 