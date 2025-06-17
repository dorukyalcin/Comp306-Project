import random
import math
from datetime import datetime
from decimal import Decimal
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User

class Plinko:
    """
    Plinko Game Implementation
    
    Features:
    - 16-row Plinko board
    - Ball physics simulation
    - Multiplier slots at the bottom
    - Dynamic ball path generation
    """
    
    def __init__(self):
        # Board configuration - 16 rows as specified in database
        self.rows = 16
        # Multipliers will be generated based on risk level
        self.risk_multipliers = self._generate_risk_multipliers()
        
        # Color scheme for slots based on multiplier value
        self.slot_colors = {
            'very_low': "#ff4757",    # Red - losing bets (< 1.0)
            'low': "#ffa502",         # Orange - small wins (1.0-2.0)  
            'medium': "#3742fa",      # Blue - medium wins (2.0-10.0)
            'high': "#7bed9f",        # Green - high wins (10.0-100.0)
            'extreme': "#ffd700"      # Gold - astronomical wins (>100.0)
        }
    
    def _generate_risk_multipliers(self):
        """Generate gaussian distributed multipliers for different risk levels"""
        # 17 slots total for 16-row Plinko board
        positions = list(range(17))
        center = 8  # Center position
        
        risk_configs = {
            'low': {
                'center_multipliers': [0.5, 0.6, 0.7, 0.8, 0.9],
                'edge_multipliers': [5, 10, 20, 50],
                'progression': 1.3
            },
            'medium': {
                'center_multipliers': [0.3, 0.4, 0.5, 0.6, 0.8],
                'edge_multipliers': [10, 25, 50, 100],
                'progression': 1.5
            },
            'high': {
                'center_multipliers': [0.2, 0.3, 0.4, 0.5, 0.7],
                'edge_multipliers': [20, 50, 100, 1000],
                'progression': 2.0
            }
        }
        
        multiplier_sets = {}
        
        for risk, config in risk_configs.items():
            multipliers = [0.0] * 17
            
            # Set center multipliers (losing positions)
            center_mults = config['center_multipliers']
            multipliers[center] = center_mults[2]  # Main center
            multipliers[center-1] = center_mults[1]
            multipliers[center+1] = center_mults[1] 
            multipliers[center-2] = center_mults[0]
            multipliers[center+2] = center_mults[0]
            
            # Set edge multipliers (extreme winning positions)
            edge_mults = config['edge_multipliers']
            multipliers[0] = edge_mults[3]    # Far left
            multipliers[16] = edge_mults[3]   # Far right
            multipliers[1] = edge_mults[2]
            multipliers[15] = edge_mults[2]
            multipliers[2] = edge_mults[1]
            multipliers[14] = edge_mults[1]
            multipliers[3] = edge_mults[0]
            multipliers[13] = edge_mults[0]
            
            # Fill remaining positions with progressive multipliers
            prog = config['progression']
            multipliers[4] = round(center_mults[0] * prog, 1)
            multipliers[12] = round(center_mults[0] * prog, 1)
            multipliers[5] = round(center_mults[1] * prog, 1)
            multipliers[11] = round(center_mults[1] * prog, 1)
            multipliers[6] = round(center_mults[2] * prog, 1)
            multipliers[10] = round(center_mults[2] * prog, 1)
            multipliers[7] = round(center_mults[3], 1)
            multipliers[9] = round(center_mults[3], 1)
            
            multiplier_sets[risk] = multipliers
            
        return multiplier_sets
    
    def get_game(self):
        """Get the Plinko game from database"""
        try:
            return Game.query.filter_by(code='PLINKO').first()
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
                return {'valid': False, 'message': 'Plinko game not found'}
            if not game.is_active:
                return {'valid': False, 'message': 'Plinko game is not active'}
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'message': f'Error validating game setup: {str(e)}'}
    
    def start_new_round(self):
        """Start a new round of Plinko"""
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
    
    def get_board_data(self, risk_level='high'):
        """Get board configuration data for frontend"""
        multipliers = self.risk_multipliers[risk_level]
        slot_names = [f"{mult}x" for mult in multipliers]
        
        # Assign colors based on multiplier values
        slot_colors = {}
        for i, mult in enumerate(multipliers):
            if mult < 1.0:
                slot_colors[mult] = self.slot_colors['very_low']
            elif mult < 2.0:
                slot_colors[mult] = self.slot_colors['low']
            elif mult < 10.0:
                slot_colors[mult] = self.slot_colors['medium']
            elif mult < 100.0:
                slot_colors[mult] = self.slot_colors['high']
            else:
                slot_colors[mult] = self.slot_colors['extreme']
        
        return {
            'rows': self.rows,
            'multipliers': multipliers,
            'slot_names': slot_names,
            'slot_colors': slot_colors,
            'risk_levels': list(self.risk_multipliers.keys())
        }
    
    def place_bet(self, user_id, bet_amount, risk_level='high', wallet_id=None):
        """Place a bet and drop the ball"""
        try:
            if bet_amount <= 0:
                return {'success': False, 'message': 'Bet amount must be positive'}
            
            # Convert bet_amount to Decimal for database operations
            bet_amount = Decimal(str(bet_amount))
            
            # Validate risk level
            if risk_level not in self.risk_multipliers:
                risk_level = 'high'
            
            # Get game
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            # Get or create active round
            active_round = self.get_active_round()
            if not active_round:
                result = self.start_new_round()
                if not result['success']:
                    return result
                active_round = self.get_active_round()
            
            # Get user's wallet
            user = User.query.get(user_id)
            if not user or not user.wallets:
                return {'success': False, 'message': 'User wallet not found'}
            
            # Use the specified wallet or primary wallet
            if wallet_id:
                wallet = Wallet.query.filter_by(wallet_id=wallet_id, user_id=user_id).first()
                if not wallet:
                    return {'success': False, 'message': 'Specified wallet not found'}
            else:
                wallet = user.get_primary_wallet()
            
            if wallet.balance < bet_amount:
                return {'success': False, 'message': 'Insufficient funds'}
            
            # Simulate ball drop with risk-specific multipliers
            ball_result = self._simulate_ball_drop(risk_level)
            
            # Create bet
            bet = Bet(
                round_id=active_round.round_id,
                user_id=user_id,
                amount=bet_amount,
                choice_data={'ball_path': ball_result['path'], 'risk_level': risk_level},
                settled_at=datetime.now()
            )
            db.session.add(bet)
            
            # Create outcome
            outcome = Outcome(
                round_id=active_round.round_id,
                outcome_data={
                    'final_slot': ball_result['final_slot'],
                    'multiplier': ball_result['multiplier'],
                    'ball_path': ball_result['path'],
                    'risk_level': risk_level
                },
                payout_multiplier=Decimal(str(ball_result['multiplier']))
            )
            db.session.add(outcome)
            
            # Update wallet balance
            wallet.balance -= bet_amount
            
            # Create bet transaction (money going out of wallet)
            bet_transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=bet_amount,
                txn_type='bet'
            )
            db.session.add(bet_transaction)
            
            # Handle winnings if any
            win_amount = Decimal('0')
            if ball_result['multiplier'] > 0:
                win_amount = bet_amount * Decimal(str(ball_result['multiplier']))
                wallet.balance += win_amount
                
                # Create win transaction (money coming into wallet)
                win_transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=win_amount,
                    txn_type='win'
                )
                db.session.add(win_transaction)
            
            db.session.commit()
            
            return {
                'success': True,
                'ball_path': ball_result['path'],
                'final_slot': ball_result['final_slot'],
                'multiplier': ball_result['multiplier'],
                'slot_name': ball_result['slot_name'],
                'win_amount': float(win_amount) if win_amount > 0 else 0,
                'wallet_balance': float(wallet.balance),
                'wallet_currency': wallet.currency
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error placing bet: {str(e)}'}
    
    def _simulate_ball_drop(self, risk_level='high'):
        """Simulate a ball dropping through the Plinko board"""
        # Start at the center of the top (position 8 for 16-row board)
        position = 8.0
        path = []
        
        # Get multipliers for this risk level
        multipliers = self.risk_multipliers[risk_level]
        slot_names = [f"{mult}x" for mult in multipliers]
        
        # For each row, determine if ball goes left or right
        for row in range(self.rows):
            # Add slight bias toward center to make extreme outcomes less common
            center_bias = 0.1 if abs(position - 8) > 4 else 0
            
            # Random choice with center bias
            if random.random() < (0.5 + center_bias):
                direction = 0.5  # Go right
            else:
                direction = -0.5  # Go left
            
            position += direction
            
            # Ensure position stays within bounds
            position = max(0, min(16, position))
            
            path.append({
                'row': row,
                'position': position,
                'direction': 'right' if direction > 0 else 'left'
            })
        
        # Final slot is determined by the final position
        final_slot = int(round(position))
        final_slot = max(0, min(len(multipliers) - 1, final_slot))
        
        return {
            'path': path,
            'final_slot': final_slot,
            'multiplier': multipliers[final_slot],
            'slot_name': slot_names[final_slot]
        }
    
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
    
    def get_statistics(self, risk_level='high'):
        """Get game statistics for display"""
        try:
            game = self.get_game()
            if not game:
                return {'error': 'Game not found'}
            
            # Get multipliers for this risk level
            multipliers = self.risk_multipliers[risk_level]
            
            # Calculate theoretical RTP based on multipliers
            # Assuming gaussian probability distribution (center more likely)
            total_prob = 0
            weighted_return = 0
            
            for i, mult in enumerate(multipliers):
                # Gaussian probability - center slots more likely
                distance_from_center = abs(i - 8)
                prob = math.exp(-0.5 * (distance_from_center / 3) ** 2)
                total_prob += prob
                weighted_return += mult * prob
            
            # Normalize
            avg_multiplier = weighted_return / total_prob if total_prob > 0 else 1
            theoretical_rtp = avg_multiplier * 100
            
            return {
                'total_slots': len(multipliers),
                'max_multiplier': max(multipliers),
                'min_multiplier': min(multipliers),
                'avg_multiplier': round(avg_multiplier, 2),
                'theoretical_rtp': round(theoretical_rtp, 1),
                'house_edge': round((1 - avg_multiplier) * 100, 1),
                'risk_level': risk_level
            }
        except Exception as e:
            return {'error': f'Error getting statistics: {str(e)}'} 