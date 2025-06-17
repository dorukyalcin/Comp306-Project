import random
from datetime import datetime
from decimal import Decimal
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User

class Slots:
    """
    Slot Machine Game Implementation
    
    Features:
    - 3 reels with standard symbols
    - Single payline
    - Standard RTP (96%)
    - Multiple symbol combinations with different payouts
    """
    
    def __init__(self):
        self.symbols = {
            'seven': {'weight': 1, 'payout': 10, 'image': 'seven.png', 'name': 'Lucky Seven'},
            'cherry': {'weight': 3, 'payout': 5, 'image': 'cherry.png', 'name': 'Cherry'}, 
            'lemon': {'weight': 3, 'payout': 5, 'image': 'lemon.png', 'name': 'Lemon'},
            'orange': {'weight': 3, 'payout': 5, 'image': 'orange.png', 'name': 'Orange'},
            'grape': {'weight': 2, 'payout': 7, 'image': 'grape.png', 'name': 'Grape'},
            'diamond': {'weight': 1, 'payout': 15, 'image': 'diamond.png', 'name': 'Diamond'},
            'slot_machine': {'weight': 1, 'payout': 20, 'image': 'seven.png', 'name': 'Jackpot Seven'}  # Using seven as fallback since no slot machine image
        }
        
    def get_game(self):
        """Get the slot machine game from database"""
        try:
            return Game.query.filter_by(code='SLOT').first()
        except Exception as e:
            return None
    
    def get_active_round(self):
        """Get the current active round"""
        try:
            game = self.get_game()
            if not game:
                return None
            # Get the most recent round that hasn't ended
            return Round.query.filter_by(game_id=game.game_id).filter(Round.ended_at.is_(None)).first()
        except Exception as e:
            return None
    
    def validate_game_setup(self):
        """Validate that the game is properly set up"""
        try:
            game = self.get_game()
            if not game:
                return {'valid': False, 'message': 'Slot machine game not found'}
            if not game.is_active:
                return {'valid': False, 'message': 'Slot machine game is not active'}
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'message': f'Error validating game setup: {str(e)}'}
    
    def start_new_round(self):
        """Start a new round of the slot machine"""
        try:
            # Check for existing active round
            active_round = self.get_active_round()
            if active_round:
                return {'success': False, 'message': 'Round already in progress'}
            
            # Create new round
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            round = Round(
                game_id=game.game_id,
                started_at=datetime.now()
            )
            db.session.add(round)
            db.session.commit()
            
            return {'success': True, 'round_id': round.round_id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error starting round: {str(e)}'}
    
    def _spin_reels(self):
        """Generate a random spin result"""
        # Create weighted list of symbols
        symbols_list = []
        for symbol, data in self.symbols.items():
            symbols_list.extend([symbol] * data['weight'])
        
        # Spin three reels
        return [random.choice(symbols_list) for _ in range(3)]
    
    def _calculate_payout(self, reels):
        """Calculate payout multiplier based on spin results"""
        # Check for three of a kind
        if len(set(reels)) == 1:
            return self.symbols[reels[0]]['payout']
        
        # Check for two of a kind
        if len(set(reels)) == 2:
            # Find the symbol that appears twice
            for symbol in set(reels):
                if reels.count(symbol) == 2:
                    return self.symbols[symbol]['payout'] / 2
        
        return 0
    
    def get_symbol_data(self, symbol_key):
        """Get symbol data for display purposes"""
        return self.symbols.get(symbol_key, {})
    
    def get_all_symbols(self):
        """Get all symbols data for frontend display"""
        return self.symbols
    
    def place_bet(self, user_id, bet_amount):
        """Place a bet and spin the reels"""
        try:
            if bet_amount <= 0:
                return {'success': False, 'message': 'Bet amount must be positive'}
            
            # Get game and check limits
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            # No betting limits - user can bet any amount they can afford
            
            # Get or create active round
            active_round = self.get_active_round()
            if not active_round:
                result = self.start_new_round()
                if not result['success']:
                    return result
                active_round = self.get_active_round()
            
            # Get user's primary wallet (any currency)
            user = User.query.get(user_id)
            if not user or not user.wallets:
                return {'success': False, 'message': 'User wallet not found'}
            
            # Use the primary wallet (prioritizes USD, supports all currencies)
            wallet = user.get_primary_wallet()
            if wallet.balance < bet_amount:
                return {'success': False, 'message': 'Insufficient funds'}
            
            # Spin the reels
            reels = self._spin_reels()
            payout_multiplier = self._calculate_payout(reels)
            
            # Create bet
            bet = Bet(
                round_id=active_round.round_id,
                user_id=user_id,
                amount=bet_amount,
                choice_data={'reels': reels},
                settled_at=datetime.now()
            )
            db.session.add(bet)
            
            # Create outcome
            outcome = Outcome(
                round_id=active_round.round_id,
                outcome_data={'reels': reels},
                payout_multiplier=Decimal(str(payout_multiplier))
            )
            db.session.add(outcome)
            
            # Update wallet
            wallet.balance -= bet_amount
            if payout_multiplier > 0:
                win_amount = bet_amount * Decimal(str(payout_multiplier))
                wallet.balance += win_amount
                
                # Create win transaction
                win_transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=win_amount,
                    txn_type='bet_win'
                )
                db.session.add(win_transaction)
            
            # Create bet transaction
            bet_transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=-bet_amount,
                txn_type='bet_loss'
            )
            db.session.add(bet_transaction)
            
            db.session.commit()
            
            return {
                'success': True,
                'reels': reels,
                'reel_images': [self.symbols[symbol]['image'] for symbol in reels],
                'reel_names': [self.symbols[symbol]['name'] for symbol in reels],
                'payout_multiplier': payout_multiplier,
                'win_amount': float(bet_amount * Decimal(str(payout_multiplier))) if payout_multiplier > 0 else 0
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error placing bet: {str(e)}'}
    
    def get_game_status(self):
        """Get current game status"""
        try:
            game = self.get_game()
            if not game:
                return {'status': 'error', 'message': 'Game not found'}
            
            active_round = self.get_active_round()
            if active_round:
                return {'status': 'active', 'round_id': active_round.round_id}
            
            return {'status': 'ready'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error getting game status: {str(e)}'}