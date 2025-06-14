import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User, Horse, HorseRunner, HorseResult


class HorseRacing:
    """
    Horse Racing Game Logic Handler
    
    This class manages all horse racing functionality including:
    - Starting new races with real horse data
    - Managing betting on specific horses
    - Running races and determining winners based on horse stats
    - Calculating payouts based on odds
    - Race status management with detailed horse information
    """
    
    def __init__(self):
        self.game_code = 'HORSE'
        self.num_horses = 6
        
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
    
    def _calculate_horse_odds(self, horse):
        """
        Calculate odds for a horse based on their stats
        
        Args:
            horse (Horse): Horse model instance
            
        Returns:
            Decimal: Calculated odds
        """
        # Base odds calculation based on horse stats
        base_odds = Decimal('2.0')
        
        # Age factor (younger horses have slightly better odds in general)
        age_factor = Decimal('1.0')
        if horse.age <= 4:
            age_factor = Decimal('0.9')  # Better odds for young horses
        elif horse.age >= 10:
            age_factor = Decimal('1.2')  # Worse odds for older horses
            
        # Speed factor (higher speed = better odds)
        speed_factor = Decimal('1.0')
        if horse.base_speed >= Decimal('8.0'):
            speed_factor = Decimal('0.8')  # Better odds for fast horses
        elif horse.base_speed <= Decimal('5.0'):
            speed_factor = Decimal('1.3')  # Worse odds for slow horses
            
        # Temperament factor
        temperament_factors = {
            'calm': Decimal('0.9'),
            'aggressive': Decimal('1.1'),
            'nervous': Decimal('1.2'),
            'confident': Decimal('0.8'),
            'unpredictable': Decimal('1.3')
        }
        temperament_factor = temperament_factors.get(horse.temperament.lower(), Decimal('1.0'))
        
        # Add some randomness (±0.3)
        random_factor = Decimal(str(random.uniform(0.7, 1.3)))
        
        # Calculate final odds
        odds = base_odds * age_factor * speed_factor * temperament_factor * random_factor
        
        # Ensure odds are within reasonable range (1.2 to 8.0)
        odds = max(Decimal('1.2'), min(odds, Decimal('8.0')))
        
        return round(odds, 2)
    
    def start_new_race(self):
        """
        Start a new horse race round with real horses
        
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
            
            # Get available horses from database
            available_horses = Horse.query.all()
            if len(available_horses) < self.num_horses:
                return {'success': False, 'message': f'Not enough horses in database. Need {self.num_horses}, found {len(available_horses)}'}
            
            # Select random horses for this race
            race_horses = random.sample(available_horses, self.num_horses)
            
            # Create new round
            new_round = Round(
                game_id=game.game_id,
                started_at=datetime.now(),
                rng_seed=f"horse_seed_{random.randint(100000, 999999)}"
            )
            db.session.add(new_round)
            db.session.flush()  # Get the round_id
            
            # Create horse runners for this race
            for i, horse in enumerate(race_horses, 1):
                odds = self._calculate_horse_odds(horse)
                
                horse_runner = HorseRunner(
                    round_id=new_round.round_id,
                    horse_id=horse.horse_id,
                    lane_no=i,
                    odds=odds
                )
                db.session.add(horse_runner)
            
            db.session.commit()
            
            return {'success': True, 'round_id': new_round.round_id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error starting race: {str(e)}'}
    
    def place_bet(self, user_id, horse_id, bet_amount, bet_type='win'):
        """
        Place a bet on a horse
        
        Args:
            user_id (int): ID of the user placing the bet
            horse_id (int): ID of the horse to bet on
            bet_amount (Decimal): Amount to bet
            bet_type (str): Type of bet ('win', 'place', 'show')
            
        Returns:
            dict: Success status and message
        """
        try:
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
            
            # Validate that the horse is actually running in this race
            horse_runner = HorseRunner.query.filter_by(
                round_id=active_round.round_id,
                horse_id=horse_id
            ).first()
            
            if not horse_runner:
                return {'success': False, 'message': 'Selected horse is not running in this race'}
            
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
            
            # Create bet with horse_id and lane information
            bet = Bet(
                round_id=active_round.round_id,
                user_id=user_id,
                amount=bet_amount,
                choice_data={
                    'bet_type': bet_type, 
                    'horse_id': horse_id,
                    'lane_no': horse_runner.lane_no,
                    'odds': float(horse_runner.odds)
                },
                placed_at=datetime.now()
            )
            db.session.add(bet)
            db.session.commit()
            
            return {'success': True, 'message': 'Bet placed successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error placing bet: {str(e)}'}
    
    def _simulate_race_times(self, horse_runners):
        """
        Simulate race times for horses based on their stats
        
        Args:
            horse_runners (list): List of HorseRunner objects
            
        Returns:
            dict: horse_id -> race_time mapping
        """
        race_times = {}
        
        for runner in horse_runners:
            horse = runner.horse
            
            # Base time calculation (lower is better)
            base_time = float(20.0 - horse.base_speed)  # 20 seconds base minus speed
            
            # Add randomness based on temperament
            temperament_variance = {
                'calm': 0.5,
                'confident': 0.3,
                'aggressive': 0.8,
                'nervous': 1.2,
                'unpredictable': 1.5
            }
            
            variance = temperament_variance.get(horse.temperament.lower(), 1.0)
            random_factor = random.uniform(-variance, variance)
            
            # Age factor (prime age is 4-8)
            age_factor = 0
            if horse.age < 4:
                age_factor = 0.5  # Young horses may be inconsistent
            elif horse.age > 10:
                age_factor = 1.0  # Older horses may be slower
                
            final_time = base_time + random_factor + age_factor
            
            # Ensure times are within reasonable range (15-30 seconds)
            final_time = max(15.0, min(final_time, 30.0))
            
            race_times[runner.horse_id] = round(final_time, 2)
            
        return race_times

    def run_race(self):
        """
        Execute the horse race and determine winner based on horse stats
        
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
            
            # Get horse runners for this race
            horse_runners = HorseRunner.query.filter_by(round_id=active_round.round_id).all()
            if not horse_runners:
                return {'success': False, 'message': 'No horses in this race'}
            
            # Simulate the race
            race_times = self._simulate_race_times(horse_runners)
            
            # Sort horses by race time (fastest first)
            sorted_results = sorted(race_times.items(), key=lambda x: x[1])
            
            # Create horse results
            for position, (horse_id, race_time) in enumerate(sorted_results, 1):
                runner = next(r for r in horse_runners if r.horse_id == horse_id)
                
                horse_result = HorseResult(
                    round_id=active_round.round_id,
                    horse_id=horse_id,
                    lane_no=runner.lane_no,
                    finish_place=position,
                    race_time_sec=Decimal(str(race_time))
                )
                db.session.add(horse_result)
            
            # Create outcome with race order
            winner_horse_id = sorted_results[0][0]
            outcome_data = {
                'winner_horse_id': winner_horse_id,
                'finish_order': [horse_id for horse_id, _ in sorted_results],
                'race_times': race_times
            }
            
            outcome = Outcome(
                round_id=active_round.round_id,
                outcome_data=outcome_data,
                payout_multiplier=Decimal('2.5')  # Base multiplier, will be adjusted per bet
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
                
                # Check if bet won based on bet type
                bet_horse_id = bet.choice_data['horse_id']
                bet_type = bet.choice_data.get('bet_type', 'win')
                
                won = False
                if bet_type == 'win':
                    # Horse must finish first
                    won = (bet_horse_id == winner_horse_id)
                elif bet_type == 'place':
                    # Horse must finish in top 2
                    won = (bet_horse_id in outcome_data['finish_order'][:2])
                elif bet_type == 'show':
                    # Horse must finish in top 3
                    won = (bet_horse_id in outcome_data['finish_order'][:3])
                
                if won:
                    # Calculate payout based on original odds from the bet
                    original_odds = Decimal(str(bet.choice_data.get('odds', 2.5)))
                    payout = bet.amount * original_odds
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
                        'horse_id': bet_horse_id,
                        'lane_no': bet.choice_data.get('lane_no'),
                        'bet_amount': float(bet.amount),
                        'payout': float(payout),
                        'odds': float(original_odds)
                    })
                else:
                    bet.payout_amount = Decimal('0')
            
            db.session.commit()
            
            return {
                'success': True,
                'winner_horse_id': winner_horse_id,
                'finish_order': outcome_data['finish_order'],
                'race_times': outcome_data['race_times'],
                'round_id': active_round.round_id,
                'winners': winners,
                'total_bets': len(bets)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error running race: {str(e)}'}
    
    def get_race_status(self, user_id=None):
        """
        Get current race status with detailed horse information
        
        Args:
            user_id (int, optional): User ID to check for user-specific bet info
            
        Returns:
            dict: Race status information including horses and their details
        """
        try:
            active_round = self.get_active_round()
            
            if active_round:
                # Count bets in this round
                bet_count = Bet.query.filter_by(round_id=active_round.round_id).count()
                
                # Get horse runners for this race
                horse_runners = HorseRunner.query.filter_by(round_id=active_round.round_id).all()
                
                # Format horse information
                horses = []
                for runner in horse_runners:
                    horses.append({
                        'horse_id': runner.horse_id,
                        'name': runner.horse.name,
                        'age': runner.horse.age,
                        'base_speed': float(runner.horse.base_speed),
                        'temperament': runner.horse.temperament,
                        'lane_no': runner.lane_no,
                        'odds': float(runner.odds)
                    })
                
                status = {
                    'active': True,
                    'round_id': active_round.round_id,
                    'bet_count': bet_count,
                    'started_at': active_round.started_at.isoformat(),
                    'horses': horses,
                    'user_has_bet': False,
                    'user_bet': None
                }
                
                # Check user-specific info if user_id provided
                if user_id:
                    user_bet = Bet.query.filter_by(round_id=active_round.round_id, user_id=user_id).first()
                    if user_bet:
                        status['user_has_bet'] = True
                        horse_id = user_bet.choice_data['horse_id']
                        odds = Decimal(str(user_bet.choice_data.get('odds', 2.5)))
                        
                        status['user_bet'] = {
                            'horse_id': horse_id,
                            'lane_no': user_bet.choice_data.get('lane_no'),
                            'bet_type': user_bet.choice_data.get('bet_type', 'win'),
                            'amount': float(user_bet.amount),
                            'odds': float(odds),
                            'potential_payout': float(user_bet.amount * odds)
                        }
                
                return status
            else:
                return {'active': False}
                
        except Exception as e:
            return {'active': False, 'error': str(e)}
    
    def get_horse_info(self):
        """
        Get information about all horses in the database
        
        Returns:
            dict: Horse information with stats and details
        """
        try:
            horses = Horse.query.all()
            
            horse_data = []
            for horse in horses:
                # Calculate recent performance (simplified)
                recent_results = HorseResult.query.filter_by(horse_id=horse.horse_id)\
                                                .order_by(HorseResult.round_id.desc())\
                                                .limit(5).all()
                
                avg_finish = sum(r.finish_place for r in recent_results) / len(recent_results) if recent_results else 0
                
                horse_data.append({
                    'horse_id': horse.horse_id,
                    'name': horse.name,
                    'age': horse.age,
                    'base_speed': float(horse.base_speed),
                    'temperament': horse.temperament,
                    'races_run': len(recent_results),
                    'avg_finish': round(avg_finish, 2) if avg_finish else None,
                    'emoji': '🐴' if horse.horse_id % 2 == 1 else ('🐎' if horse.horse_id % 3 == 0 else '🏇')
                })
            
            return {
                'horses': horse_data,
                'total_horses': len(horses)
            }
            
        except Exception as e:
            return {'error': str(e), 'horses': [], 'total_horses': 0}
    
    def get_betting_stats(self, round_id=None):
        """
        Get betting statistics for a specific round or current active round
        
        Args:
            round_id (int, optional): Specific round ID
            
        Returns:
            dict: Betting statistics with horse details
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
            
            # Get horse runners for this round
            horse_runners = HorseRunner.query.filter_by(round_id=target_round.round_id).all()
            
            # Initialize horse betting stats
            horse_bets = {}
            for runner in horse_runners:
                horse_bets[runner.horse_id] = {
                    'count': 0,
                    'amount': Decimal('0'),
                    'name': runner.horse.name,
                    'lane_no': runner.lane_no,
                    'odds': float(runner.odds)
                }
            
            # Count bets per horse
            for bet in bets:
                horse_id = bet.choice_data['horse_id']
                if horse_id in horse_bets:
                    horse_bets[horse_id]['count'] += 1
                    horse_bets[horse_id]['amount'] += bet.amount
            
            # Convert to serializable format
            horse_bets_formatted = {}
            for horse_id, stats in horse_bets.items():
                horse_bets_formatted[horse_id] = {
                    'count': stats['count'],
                    'amount': float(stats['amount']),
                    'name': stats['name'],
                    'lane_no': stats['lane_no'],
                    'odds': stats['odds']
                }
            
            return {
                'round_id': target_round.round_id,
                'total_bets': total_bets,
                'total_amount': float(total_amount),
                'horse_bets': horse_bets_formatted,
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