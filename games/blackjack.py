import random
import os
from datetime import datetime
from decimal import Decimal
from models import db, Game, Round, Bet, Outcome, Wallet, Transaction, User

class Blackjack:
    """
    Blackjack Game Implementation
    
    Features:
    - Standard 52-card deck
    - Dealer stands on 17
    - Blackjack pays 3:2
    - Hit, Stand, Double Down actions
    - Proper card value calculations
    - Ace handling (1 or 11)
    """
    
    def __init__(self):
        self.game_code = 'BJ21'
        self.deck = self._create_deck()
        self.card_values = {
            'A': [1, 11], '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
            '10': 10, 'J': 10, 'Q': 10, 'K': 10
        }
        
    def _create_deck(self):
        """Create a standard 52-card deck"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        deck = []
        for suit in suits:
            for rank in ranks:
                # Map card to image filename - use the version without "2" suffix
                if rank == 'A':
                    filename = f'ace_of_{suit}.png'
                elif rank in ['J', 'Q', 'K']:
                    filename = f'{rank.lower()}_of_{suit}.png'
                else:
                    filename = f'{rank}_of_{suit}.png'
                
                deck.append({
                    'rank': rank,
                    'suit': suit,
                    'image': filename,
                    'display_name': f'{rank} of {suit.title()}'
                })
        
        return deck
    
    def _shuffle_deck(self):
        """Shuffle the deck"""
        random.shuffle(self.deck)
    
    def _deal_card(self):
        """Deal a card from the deck"""
        if not self.deck:
            self.deck = self._create_deck()
            self._shuffle_deck()
        return self.deck.pop()
    
    def _calculate_hand_value(self, hand):
        """Calculate the value of a hand, handling Aces properly"""
        total = 0
        aces = 0
        
        for card in hand:
            rank = card['rank']
            if rank == 'A':
                aces += 1
                total += 11  # Start with 11 for Ace
            else:
                total += self.card_values[rank]
        
        # Adjust for Aces if total is over 21
        while total > 21 and aces > 0:
            total -= 10  # Convert Ace from 11 to 1
            aces -= 1
        
        return total
    
    def _is_blackjack(self, hand):
        """Check if hand is a blackjack (21 with 2 cards)"""
        return len(hand) == 2 and self._calculate_hand_value(hand) == 21
    
    def _is_bust(self, hand):
        """Check if hand is bust (over 21)"""
        return self._calculate_hand_value(hand) > 21
    
    def get_game(self):
        """Get the Blackjack game from database"""
        try:
            return Game.query.filter_by(code=self.game_code).first()
        except Exception as e:
            return None
    
    def get_active_round(self):
        """Get the current active round"""
        try:
            game = self.get_game()
            if not game:
                return None
            return Round.query.filter_by(game_id=game.game_id).filter(Round.ended_at.is_(None)).first()
        except Exception as e:
            return None
    
    def validate_game_setup(self):
        """Validate that the game is properly set up"""
        try:
            game = self.get_game()
            if not game:
                return {'valid': False, 'message': 'Blackjack game not found'}
            if not game.is_active:
                return {'valid': False, 'message': 'Blackjack game is not active'}
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'message': f'Error validating game setup: {str(e)}'}
    
    def start_new_round(self):
        """Start a new round of Blackjack"""
        try:
            # Check for existing active round
            active_round = self.get_active_round()
            if active_round:
                return {'success': False, 'message': 'Round already in progress'}
            
            # Create new round
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            # Shuffle deck for new round
            self._shuffle_deck()
            
            round = Round(
                game_id=game.game_id,
                started_at=datetime.now(),
                rng_seed=str(random.randint(1000000, 9999999))
            )
            db.session.add(round)
            db.session.commit()
            
            return {'success': True, 'round_id': round.round_id}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error starting round: {str(e)}'}
    
    def deal_initial_hand(self):
        """Deal initial 2 cards to player and dealer"""
        try:
            # Ensure we have a fresh deck
            self.deck = self._create_deck()
            self._shuffle_deck()
            
            # Deal 2 cards to player, 2 to dealer
            player_hand = [self._deal_card(), self._deal_card()]
            dealer_hand = [self._deal_card(), self._deal_card()]
            
            return {
                'success': True,
                'player_hand': player_hand,
                'dealer_hand': dealer_hand,
                'player_value': self._calculate_hand_value(player_hand),
                'dealer_showing': self._calculate_hand_value([dealer_hand[0]]),  # Only first card
                'player_blackjack': self._is_blackjack(player_hand),
                'dealer_blackjack': self._is_blackjack(dealer_hand)
            }
        except Exception as e:
            return {'success': False, 'message': f'Error dealing cards: {str(e)}'}
    
    def hit(self, hand):
        """Add a card to the hand"""
        try:
            new_card = self._deal_card()
            hand.append(new_card)
            
            return {
                'success': True,
                'new_card': new_card,
                'hand': hand,
                'hand_value': self._calculate_hand_value(hand),
                'is_bust': self._is_bust(hand)
            }
        except Exception as e:
            return {'success': False, 'message': f'Error hitting: {str(e)}'}
    
    def dealer_play(self, dealer_hand):
        """Play dealer's hand according to rules (stand on 17)"""
        try:
            actions = []
            
            while self._calculate_hand_value(dealer_hand) < 17:
                new_card = self._deal_card()
                dealer_hand.append(new_card)
                actions.append({
                    'action': 'hit',
                    'card': new_card,
                    'hand_value': self._calculate_hand_value(dealer_hand)
                })
            
            final_value = self._calculate_hand_value(dealer_hand)
            actions.append({
                'action': 'stand',
                'final_value': final_value,
                'is_bust': self._is_bust(dealer_hand)
            })
            
            return {
                'success': True,
                'dealer_hand': dealer_hand,
                'dealer_value': final_value,
                'dealer_actions': actions,
                'dealer_bust': self._is_bust(dealer_hand)
            }
        except Exception as e:
            return {'success': False, 'message': f'Error in dealer play: {str(e)}'}
    
    def determine_winner(self, player_hand, dealer_hand, player_actions):
        """Determine the winner and calculate payout"""
        player_value = self._calculate_hand_value(player_hand)
        dealer_value = self._calculate_hand_value(dealer_hand)
        
        player_blackjack = self._is_blackjack(player_hand)
        dealer_blackjack = self._is_blackjack(dealer_hand)
        player_bust = self._is_bust(player_hand)
        dealer_bust = self._is_bust(dealer_hand)
        
        # Determine result
        if player_bust:
            result = 'lose'
            payout_multiplier = 0
        elif dealer_bust:
            if player_blackjack:
                result = 'blackjack'
                payout_multiplier = 2.5  # 3:2 payout
            else:
                result = 'win'
                payout_multiplier = 2
        elif player_blackjack and dealer_blackjack:
            result = 'push'
            payout_multiplier = 1
        elif player_blackjack:
            result = 'blackjack'
            payout_multiplier = 2.5  # 3:2 payout
        elif dealer_blackjack:
            result = 'lose'
            payout_multiplier = 0
        elif player_value > dealer_value:
            result = 'win'
            payout_multiplier = 2
        elif player_value < dealer_value:
            result = 'lose'
            payout_multiplier = 0
        else:
            result = 'push'
            payout_multiplier = 1
        
        return {
            'result': result,
            'payout_multiplier': payout_multiplier,
            'player_value': player_value,
            'dealer_value': dealer_value,
            'player_blackjack': player_blackjack,
            'dealer_blackjack': dealer_blackjack,
            'player_bust': player_bust,
            'dealer_bust': dealer_bust
        }
    
    def place_bet(self, user_id, bet_amount, wallet_id=None):
        """Place a bet and start a new hand"""
        try:
            if bet_amount <= 0:
                return {'success': False, 'message': 'Bet amount must be positive'}
            
            # Convert bet_amount to Decimal for database operations
            bet_amount = Decimal(str(bet_amount))
            
            # Get game
            game = self.get_game()
            if not game:
                return {'success': False, 'message': 'Game not found'}
            
            # Validate bet amount
            if bet_amount < game.min_bet or bet_amount > game.max_bet:
                return {'success': False, 'message': f'Bet must be between ${game.min_bet} and ${game.max_bet}'}
            
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
            
            # Deal initial hand
            deal_result = self.deal_initial_hand()
            if not deal_result['success']:
                return deal_result
            
            # Store complete game state for this bet
            game_state = {
                'player_hand': deal_result['player_hand'],
                'dealer_hand': deal_result['dealer_hand'],  # Store complete dealer hand
                'player_actions': [],
                'game_complete': False
            }
            
            # Check for immediate blackjack
            if deal_result['player_blackjack'] or deal_result['dealer_blackjack']:
                # Complete the game immediately
                dealer_result = self.dealer_play(deal_result['dealer_hand'].copy())
                winner_result = self.determine_winner(
                    deal_result['player_hand'], 
                    dealer_result['dealer_hand'],
                    []
                )
                game_state['game_complete'] = True
                game_state['dealer_final_hand'] = dealer_result['dealer_hand']
                game_state['result'] = winner_result
            
            # Create bet record with complete game state
            bet = Bet(
                round_id=active_round.round_id,
                user_id=user_id,
                amount=bet_amount,
                choice_data={
                    'initial_hand': deal_result['player_hand'],
                    'dealer_hand': deal_result['dealer_hand'],  # Store dealer hand in bet
                    'actions': []
                },
                settled_at=datetime.now() if game_state['game_complete'] else None
            )
            db.session.add(bet)
            db.session.flush()  # Get bet_id
            
            # Handle immediate completion (blackjack scenario)
            if game_state['game_complete']:
                result = game_state['result']
                
                # Create outcome
                outcome = Outcome(
                    round_id=active_round.round_id,
                    outcome_data={
                        'player_hand': deal_result['player_hand'],
                        'dealer_hand': game_state['dealer_final_hand'],
                        'result': result['result'],
                        'player_value': result['player_value'],
                        'dealer_value': result['dealer_value']
                    },
                    payout_multiplier=Decimal(str(result['payout_multiplier']))
                )
                db.session.add(outcome)
                db.session.flush()
                
                # Update bet with outcome
                bet.outcome_id = outcome.outcome_id
                bet.payout_amount = bet_amount * Decimal(str(result['payout_multiplier']))
                
                # Process wallet transactions
                wallet.balance -= bet_amount
                
                # Create bet transaction (money going out of wallet)
                bet_transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=bet_amount,
                    txn_type='bet'
                )
                db.session.add(bet_transaction)
                
                if result['payout_multiplier'] > 0:
                    win_amount = bet_amount * Decimal(str(result['payout_multiplier']))
                    wallet.balance += win_amount
                    
                    # Create win transaction (money coming into wallet)
                    win_transaction = Transaction(
                        wallet_id=wallet.wallet_id,
                        amount=win_amount,
                        txn_type='win'
                    )
                    db.session.add(win_transaction)
            else:
                # Deduct bet amount for ongoing game
                wallet.balance -= bet_amount
                
                # Create bet transaction (money going out of wallet)
                bet_transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=bet_amount,
                    txn_type='bet'
                )
                db.session.add(bet_transaction)
            
            db.session.commit()
            
            response = {
                'success': True,
                'bet_id': bet.bet_id,
                'player_hand': deal_result['player_hand'],
                'dealer_hand': [deal_result['dealer_hand'][0]],  # Only show first card
                'dealer_hidden_card': True,
                'player_value': deal_result['player_value'],
                'dealer_showing': deal_result['dealer_showing'],
                'player_blackjack': deal_result['player_blackjack'],
                'dealer_blackjack': deal_result['dealer_blackjack'],
                'wallet_balance': float(wallet.balance),
                'wallet_currency': wallet.currency,
                'game_complete': game_state['game_complete']
            }
            
            # Add result info if game is complete
            if game_state['game_complete']:
                response.update({
                    'dealer_hand': game_state['dealer_final_hand'],
                    'dealer_hidden_card': False,
                    'dealer_value': game_state['result']['dealer_value'],
                    'result': game_state['result']['result'],
                    'payout_multiplier': game_state['result']['payout_multiplier'],
                    'win_amount': float(bet.payout_amount) if bet.payout_amount else 0
                })
            
            return response
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error placing bet: {str(e)}'}
    
    def player_action(self, bet_id, action):
        """Handle player action (hit, stand, double)"""
        try:
            # Get the bet
            bet = Bet.query.get(bet_id)
            if not bet:
                return {'success': False, 'message': 'Bet not found'}
            
            if bet.settled_at:
                return {'success': False, 'message': 'Game already completed'}
            
            # Reconstruct game state from stored data
            player_hand = bet.choice_data['initial_hand'].copy()
            dealer_hand = bet.choice_data['dealer_hand'].copy()  # Get original dealer hand
            actions = bet.choice_data.get('actions', [])
            
            # Apply previous actions to rebuild player hand
            for prev_action in actions:
                if prev_action['action'] == 'hit':
                    player_hand.append(prev_action['card'])
            
            if action == 'hit':
                hit_result = self.hit(player_hand.copy())
                if not hit_result['success']:
                    return hit_result
                
                # Record the action
                actions.append({
                    'action': 'hit',
                    'card': hit_result['new_card']
                })
                
                # Update bet choice_data
                bet.choice_data = {
                    'initial_hand': bet.choice_data['initial_hand'],
                    'dealer_hand': bet.choice_data['dealer_hand'],  # Preserve dealer hand
                    'actions': actions
                }
                
                response = {
                    'success': True,
                    'action': 'hit',
                    'new_card': hit_result['new_card'],
                    'player_hand': hit_result['hand'],
                    'player_value': hit_result['hand_value'],
                    'is_bust': hit_result['is_bust'],
                    'game_complete': hit_result['is_bust']
                }
                
                # If bust, complete the game
                if hit_result['is_bust']:
                    response.update(self._complete_game(bet, hit_result['hand'], dealer_hand, 'bust'))
                
                db.session.commit()
                return response
                
            elif action == 'stand':
                # Complete the game
                actions.append({'action': 'stand'})
                bet.choice_data = {
                    'initial_hand': bet.choice_data['initial_hand'],
                    'dealer_hand': bet.choice_data['dealer_hand'],  # Preserve dealer hand
                    'actions': actions
                }
                
                response = {
                    'success': True,
                    'action': 'stand',
                    'game_complete': True
                }
                response.update(self._complete_game(bet, player_hand, dealer_hand, 'stand'))
                
                db.session.commit()
                return response
            
            else:
                return {'success': False, 'message': 'Invalid action'}
                
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error processing action: {str(e)}'}
    
    def _complete_game(self, bet, player_hand, original_dealer_hand, reason):
        """Complete the game and determine winner using the original dealer hand"""
        try:
            # Use the original dealer hand and play it out according to rules
            dealer_hand = original_dealer_hand.copy()
            dealer_result = self.dealer_play(dealer_hand)
            
            # Determine winner
            winner_result = self.determine_winner(player_hand, dealer_result['dealer_hand'], bet.choice_data['actions'])
            
            # Create outcome
            outcome = Outcome(
                round_id=bet.round_id,
                outcome_data={
                    'player_hand': player_hand,
                    'dealer_hand': dealer_result['dealer_hand'],
                    'result': winner_result['result'],
                    'player_value': winner_result['player_value'],
                    'dealer_value': winner_result['dealer_value'],
                    'reason': reason
                },
                payout_multiplier=Decimal(str(winner_result['payout_multiplier']))
            )
            db.session.add(outcome)
            db.session.flush()
            
            # Update bet
            bet.outcome_id = outcome.outcome_id
            bet.settled_at = datetime.now()
            bet.payout_amount = bet.amount * Decimal(str(winner_result['payout_multiplier']))
            
            # Handle winnings
            if winner_result['payout_multiplier'] > 0:
                wallet = bet.user.get_primary_wallet()
                win_amount = bet.amount * Decimal(str(winner_result['payout_multiplier']))
                wallet.balance += win_amount
                
                # Create win transaction
                win_transaction = Transaction(
                    wallet_id=wallet.wallet_id,
                    amount=win_amount,
                    txn_type='win'
                )
                db.session.add(win_transaction)
            
            return {
                'dealer_hand': dealer_result['dealer_hand'],
                'dealer_value': winner_result['dealer_value'],
                'dealer_actions': dealer_result['dealer_actions'],
                'result': winner_result['result'],
                'payout_multiplier': winner_result['payout_multiplier'],
                'win_amount': float(bet.payout_amount) if bet.payout_amount else 0,
                'wallet_balance': float(bet.user.wallets[0].balance),
                'player_value': winner_result['player_value']
            }
            
        except Exception as e:
            raise Exception(f'Error completing game: {str(e)}')
    
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
    
    def get_statistics(self):
        """Get game statistics for display"""
        try:
            game = self.get_game()
            if not game:
                return {'error': 'Game not found'}
            
            return {
                'min_bet': float(game.min_bet),
                'max_bet': float(game.max_bet),
                'house_edge': float(game.house_edge * 100),
                'blackjack_payout': '3:2',
                'dealer_rule': 'Stands on 17',
                'deck_size': 52
            }
        except Exception as e:
            return {'error': f'Error getting statistics: {str(e)}'} 