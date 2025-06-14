from abc import ABC, abstractmethod
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User
from decimal import Decimal
from datetime import datetime


class BaseGame(ABC):
    """
    Abstract base class for all casino games
    
    This class defines the standard interface that all games must implement
    to ensure consistency across the casino application.
    """
    
    def __init__(self):
        self.game_code = None  # Must be set by subclasses
        
    @abstractmethod
    def get_game(self):
        """
        Get the game from database
        
        Returns:
            Game object or None
        """
        pass
    
    @abstractmethod
    def validate_game_setup(self):
        """
        Validate that the game is properly configured
        
        Returns:
            dict: Validation result with 'valid' boolean and 'message'
        """
        pass
    
    @abstractmethod
    def get_active_round(self):
        """
        Get the currently active game round
        
        Returns:
            Round object or None
        """
        pass
    
    @abstractmethod
    def start_new_round(self):
        """
        Start a new game round
        
        Returns:
            dict: Success status and round_id or error message
        """
        pass
    
    @abstractmethod
    def place_bet(self, user_id, bet_data, bet_amount, **kwargs):
        """
        Place a bet in the game
        
        Args:
            user_id (int): ID of the user placing the bet
            bet_data (dict): Game-specific bet data
            bet_amount (Decimal): Amount to bet
            **kwargs: Additional game-specific parameters
            
        Returns:
            dict: Success status and message
        """
        pass
    
    @abstractmethod
    def execute_game(self):
        """
        Execute the game and determine outcome
        
        Returns:
            dict: Game results including winner, outcome data, etc.
        """
        pass
    
    @abstractmethod
    def get_game_status(self, user_id=None):
        """
        Get current game status
        
        Args:
            user_id (int, optional): User ID for user-specific information
            
        Returns:
            dict: Game status information
        """
        pass
    
    # Common utility methods that all games can use
    
    def _create_standard_response(self, success, message, data=None, error_code=None):
        """
        Create a standardized response format
        
        Args:
            success (bool): Whether the operation was successful
            message (str): Description of the result
            data (dict, optional): Additional data to include
            error_code (str, optional): Error code for failed operations
            
        Returns:
            dict: Standardized response
        """
        response = {
            'success': success,
            'message': message
        }
        
        if data:
            response['data'] = data
            
        if error_code and not success:
            response['error_code'] = error_code
            
        return response
    
    def _validate_user_wallet(self, user_id, required_balance=None):
        """
        Validate user exists and has a wallet
        
        Args:
            user_id (int): User ID to validate
            required_balance (Decimal, optional): Minimum required balance
            
        Returns:
            tuple: (success: bool, wallet: Wallet or None, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, None, "User not found"
            
            if not user.wallets:
                return False, None, "User wallet not found"
            
            wallet = user.wallets[0]  # Assuming first wallet
            
            if required_balance and wallet.balance < required_balance:
                return False, wallet, "Insufficient funds"
            
            return True, wallet, "Wallet validated"
            
        except Exception as e:
            return False, None, f"Error validating wallet: {str(e)}"
    
    def _create_transaction(self, wallet_id, amount, txn_type):
        """
        Create a transaction record
        
        Args:
            wallet_id (int): Wallet ID
            amount (Decimal): Transaction amount
            txn_type (str): Transaction type
            
        Returns:
            Transaction: Created transaction object
        """
        transaction = Transaction(
            wallet_id=wallet_id,
            amount=amount,
            txn_type=txn_type
        )
        db.session.add(transaction)
        return transaction
    
    def _validate_bet_amount(self, bet_amount, min_bet, max_bet):
        """
        Validate bet amount is within game limits
        
        Args:
            bet_amount (Decimal): Amount to validate
            min_bet (Decimal): Minimum allowed bet
            max_bet (Decimal): Maximum allowed bet
            
        Returns:
            tuple: (valid: bool, message: str)
        """
        if bet_amount <= 0:
            return False, "Bet amount must be positive"
        
        if bet_amount < min_bet:
            return False, f"Bet amount must be at least {min_bet}"
        
        if bet_amount > max_bet:
            return False, f"Bet amount cannot exceed {max_bet}"
        
        return True, "Bet amount is valid"
    
    def _safe_database_operation(self, operation_func, *args, **kwargs):
        """
        Execute a database operation with automatic rollback on error
        
        Args:
            operation_func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of operation_func or error response
        """
        try:
            result = operation_func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            return self._create_standard_response(
                success=False,
                message=f"Database operation failed: {str(e)}",
                error_code="DB_ERROR"
            )
    
    def get_recent_rounds(self, limit=10):
        """
        Get recent completed rounds for this game
        
        Args:
            limit (int): Maximum number of rounds to return
            
        Returns:
            list: List of recent Round objects
        """
        game = self.get_game()
        if not game:
            return []
        
        return Round.query.filter_by(game_id=game.game_id)\
                         .filter(Round.ended_at.isnot(None))\
                         .order_by(Round.ended_at.desc())\
                         .limit(limit).all()
    
    def get_game_statistics(self):
        """
        Get basic statistics for this game
        
        Returns:
            dict: Game statistics
        """
        try:
            game = self.get_game()
            if not game:
                return {'error': 'Game not found'}
            
            # Count total rounds
            total_rounds = Round.query.filter_by(game_id=game.game_id).count()
            
            # Count completed rounds
            completed_rounds = Round.query.filter_by(game_id=game.game_id)\
                                         .filter(Round.ended_at.isnot(None)).count()
            
            # Count total bets
            total_bets = db.session.query(Bet)\
                                 .join(Round)\
                                 .filter(Round.game_id == game.game_id).count()
            
            # Calculate total wagered
            total_wagered = db.session.query(db.func.sum(Bet.amount))\
                                    .join(Round)\
                                    .filter(Round.game_id == game.game_id).scalar() or Decimal('0')
            
            return {
                'game_code': self.game_code,
                'total_rounds': total_rounds,
                'completed_rounds': completed_rounds,
                'active_rounds': total_rounds - completed_rounds,
                'total_bets': total_bets,
                'total_wagered': float(total_wagered),
                'average_bet': float(total_wagered / total_bets) if total_bets > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'Error getting statistics: {str(e)}'}
            
    def __str__(self):
        """String representation of the game"""
        return f"{self.__class__.__name__}(code={self.game_code})"
    
    def __repr__(self):
        """Debug representation of the game"""
        return f"<{self.__class__.__name__}: {self.game_code}>" 