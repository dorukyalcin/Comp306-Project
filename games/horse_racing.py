import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User


class HorseRacing:
    """
    Horse Racing Game Logic Handler
    
    This class manages all horse racing functionality including:
    - Starting new races
    - Managing betting
    - Running races and determining winners
    - Calculating payouts
    - Race status management
    """
    
    def __init__(self):
        self.game_code = 'HORSE'
        self.num_horses = 6
        self.horse_names = {
            1: "Lightning Bolt",
            2: "Thunder Strike", 
            3: "Wind Runner",
            4: "Fire Dash",
            5: "Storm Chaser",
            6: "Star Galloper"
        }
        
    def get_game(self):
        """Get the horse racing game from database"""
        return Game.query.filter_by(code=self.game_code).first()
    
    def get_active_round(self):
        """Get the currently active race round"""
        game = self.get_game()
        if not game:
            return None
        return Round.query.filter_by(game_id=game.game_id, ended_at=None).first()
    
    def get_recent_rounds(self, limit=10):
        """Get recent completed race rounds"""
        game = self.get_game()
        if not game:
            return []
        return Round.query.filter_by(game_id=game.game_id)\
                         .filter(Round.ended_at.isnot(None))\
                         .order_by(Round.ended_at.desc())\
                         .limit(limit).all()
    
    def start_new_race(self):
        """
        Start a new horse race round
        
        Returns:
            dict: Success status and round_id or error message
        """
        try:
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Horse racing game not found'}
            
            # Check if there's already an active round
            active_round = self.get_active_round()
            if active_round:
                return {'success': False, 'message': 'Race already in progress'}
            
            # Create new round
            new_round = Round(
                game_id=game.game_id,
                started_at=datetime.now(),
                rng_seed=f"horse_seed_{random.randint(100000, 999999)}"
            )
            db.session.add(new_round)
            db.session.commit()
            
            return {'success': True, 'round_id': new_round.round_id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error starting race: {str(e)}'}
    
    def place_bet(self, user_id, horse_number, bet_amount, bet_type='win'):
        """
        Place a bet on a horse
        
        Args:
            user_id (int): ID of the user placing the bet
            horse_number (int): Horse number (1-6)
            bet_amount (Decimal): Amount to bet
            bet_type (str): Type of bet ('win', 'place', 'show')
            
        Returns:
            dict: Success status and message
        """
        try:
            # Validate inputs
            if not horse_number or horse_number < 1 or horse_number > self.num_horses:
                return {'success': False, 'message': 'Invalid horse selection'}
            
            if bet_amount <= 0:
                return {'success': False, 'message': 'Bet amount must be positive'}
            
            # Get game and check limits
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            if bet_amount < game.min_bet or bet_amount > game.max_bet:
                return {'success': False, 'message': f'Bet must be between {game.min_bet} and {game.max_bet}'}
            
            # Check active round
            active_round = self.get_active_round()
            if not active_round:
                return {'success': False, 'message': 'No active race'}
            
            # Get user's wallet
            user = User.query.get(user_id)
            if not user or not user.wallets:
                return {'success': False, 'message': 'User wallet not found'}
            
            wallet = user.wallets[0]
            
            # Check if user has enough balance
            if wallet.balance < bet_amount:
                return {'success': False, 'message': 'Insufficient funds'}
            
            # Check if user already has a bet in this round
            existing_bet = Bet.query.filter_by(round_id=active_round.round_id, user_id=user_id).first()
            if existing_bet:
                return {'success': False, 'message': 'You already have a bet in this race'}
            
            # Deduct bet amount from wallet
            wallet.balance -= bet_amount
            
            # Create transaction
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=bet_amount,
                txn_type='bet_placed'
            )
            db.session.add(transaction)
            
            # Create bet
            bet = Bet(
                round_id=active_round.round_id,
                user_id=user_id,
                amount=bet_amount,
                choice_data={'bet_type': bet_type, 'horse': horse_number},
                placed_at=datetime.now()
            )
            db.session.add(bet)
            db.session.commit()
            
            return {'success': True, 'message': 'Bet placed successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error placing bet: {str(e)}'}
    
    def run_race(self):
        """
        Execute the horse race and determine winner
        
        Returns:
            dict: Race results including winner, order, and round_id
        """
        try:
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            # Get active round
            active_round = self.get_active_round()
            if not active_round:
                return {'success': False, 'message': 'No active race'}
            
            # Check if there are any bets
            bets = Bet.query.filter_by(round_id=active_round.round_id).all()
            if not bets:
                return {'success': False, 'message': 'No bets placed'}
            
            # Generate race outcome
            horses = list(range(1, self.num_horses + 1))
            random.shuffle(horses)
            
            # Create outcome
            outcome = Outcome(
                round_id=active_round.round_id,
                outcome_data={'order': horses},
                payout_multiplier=Decimal('2.5')
            )
            db.session.add(outcome)
            db.session.flush()  # Get outcome ID
            
            # End the round
            active_round.ended_at = datetime.now()
            
            # Process all bets and calculate payouts
            winners = []
            for bet in bets:
                bet.settled_at = datetime.now()
                bet.outcome_id = outcome.outcome_id
                
                # Check if bet won (horse finished first)
                if bet.choice_data['horse'] == horses[0]:
                    # Winner gets payout
                    payout = bet.amount * outcome.payout_multiplier
                    bet.payout_amount = payout
                    
                    # Add to wallet
                    wallet = Wallet.query.filter_by(user_id=bet.user_id).first()
                    wallet.balance += payout
                    
                    # Create transaction
                    transaction = Transaction(
                        wallet_id=wallet.wallet_id,
                        amount=payout,
                        txn_type='bet_win'
                    )
                    db.session.add(transaction)
                    
                    winners.append({
                        'user_id': bet.user_id,
                        'horse': bet.choice_data['horse'],
                        'bet_amount': float(bet.amount),
                        'payout': float(payout)
                    })
                else:
                    bet.payout_amount = Decimal('0')
            
            db.session.commit()
            
            return {
                'success': True,
                'winner': horses[0],
                'order': horses,
                'round_id': active_round.round_id,
                'winners': winners,
                'total_bets': len(bets)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error running race: {str(e)}'}
    
    def get_race_status(self, user_id=None):
        """
        Get current race status
        
        Args:
            user_id (int, optional): User ID to check for user-specific bet info
            
        Returns:
            dict: Race status information
        """
        try:
            active_round = self.get_active_round()
            
            if active_round:
                # Count bets in this round
                bet_count = Bet.query.filter_by(round_id=active_round.round_id).count()
                
                status = {
                    'active': True,
                    'round_id': active_round.round_id,
                    'bet_count': bet_count,
                    'started_at': active_round.started_at.isoformat(),
                    'user_has_bet': False,
                    'user_bet': None
                }
                
                # Check user-specific info if user_id provided
                if user_id:
                    user_bet = Bet.query.filter_by(round_id=active_round.round_id, user_id=user_id).first()
                    if user_bet:
                        status['user_has_bet'] = True
                        status['user_bet'] = {
                            'horse': user_bet.choice_data['horse'],
                            'amount': float(user_bet.amount),
                            'potential_payout': float(user_bet.amount * Decimal('2.5'))
                        }
                
                return status
            else:
                return {'active': False}
                
        except Exception as e:
            return {'active': False, 'error': str(e)}
    
    def get_horse_info(self):
        """
        Get information about all horses
        
        Returns:
            dict: Horse information with names and numbers
        """
        return {
            'horses': [
                {
                    'number': i,
                    'name': self.horse_names[i],
                    'emoji': '🐴' if i % 2 == 1 else ('🐎' if i % 3 == 0 else '🏇')
                }
                for i in range(1, self.num_horses + 1)
            ],
            'total_horses': self.num_horses
        }
    
    def get_betting_stats(self, round_id=None):
        """
        Get betting statistics for a specific round or current active round
        
        Args:
            round_id (int, optional): Specific round ID
            
        Returns:
            dict: Betting statistics
        """
        try:
            if round_id:
                target_round = Round.query.get(round_id)
            else:
                target_round = self.get_active_round()
            
            if not target_round:
                return {'error': 'No round found'}
            
            bets = Bet.query.filter_by(round_id=target_round.round_id).all()
            
            # Calculate stats
            total_bets = len(bets)
            total_amount = sum(bet.amount for bet in bets)
            
            # Bets per horse
            horse_bets = {}
            for i in range(1, self.num_horses + 1):
                horse_bets[i] = {
                    'count': 0,
                    'amount': Decimal('0'),
                    'name': self.horse_names[i]
                }
            
            for bet in bets:
                horse_num = bet.choice_data['horse']
                horse_bets[horse_num]['count'] += 1
                horse_bets[horse_num]['amount'] += bet.amount
            
            return {
                'round_id': target_round.round_id,
                'total_bets': total_bets,
                'total_amount': float(total_amount),
                'horse_bets': {k: {
                    'count': v['count'],
                    'amount': float(v['amount']),
                    'name': v['name']
                } for k, v in horse_bets.items()},
                'average_bet': float(total_amount / total_bets) if total_bets > 0 else 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_game_setup(self):
        """
        Validate that the horse racing game is properly set up
        
        Returns:
            dict: Validation results
        """
        try:
            game = self.get_game()
            if not game:
                return {
                    'valid': False,
                    'message': 'Horse racing game not found in database',
                    'setup_required': True
                }
            
            if not game.is_active:
                return {
                    'valid': False,
                    'message': 'Horse racing game is not active',
                    'setup_required': False
                }
            
            return {
                'valid': True,
                'message': 'Horse racing game is properly configured',
                'game_info': {
                    'min_bet': float(game.min_bet),
                    'max_bet': float(game.max_bet),
                    'house_edge': float(game.house_edge),
                    'rules': game.payout_rule_json
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error validating game setup: {str(e)}',
                'setup_required': True  
            } 