from app import db
from sqlalchemy.dialects.postgresql import JSON, NUMERIC
from sqlalchemy import ForeignKey

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)
    wallets = db.relationship('Wallet', back_populates='user')
    bets = db.relationship('Bet', back_populates='user')

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    sarcasm_level = db.Column(db.SmallInteger)
    theme = db.Column(db.Text)
    user = db.relationship('User', back_populates='settings')
    sarcas_template_id = db.Column(db.Integer, db.ForeignKey('sarcastemps.template_id'))
    sarcas_template = db.relationship('SarcasTemp', back_populates='user_settings')

class Wallet(db.Model):
    __tablename__ = 'wallets'
    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    currency = db.Column(db.String)
    balance = db.Column(NUMERIC)
    user = db.relationship('User', back_populates='wallets')
    transactions = db.relationship('Transaction', back_populates='wallet')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    txn_id = db.Column(db.BigInteger, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.wallet_id'))
    amount = db.Column(NUMERIC)
    txn_type = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    wallet = db.relationship('Wallet', back_populates='transactions')

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True)
    house_edge = db.Column(NUMERIC)
    min_bet = db.Column(NUMERIC)
    max_bet = db.Column(NUMERIC)
    is_active = db.Column(db.Boolean, default=True)
    payout_rule_json = db.Column(JSON)
    rounds = db.relationship('Round', back_populates='game')

class Round(db.Model):
    __tablename__ = 'rounds'
    round_id = db.Column(db.BigInteger, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    started_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    ended_at = db.Column(db.DateTime(timezone=True))
    rng_seed = db.Column(db.String)
    game = db.relationship('Game', back_populates='rounds')
    bets = db.relationship('Bet', back_populates='round')
    outcome = db.relationship('Outcome', back_populates='round', uselist=False)

class Outcome(db.Model):
    __tablename__ = 'outcomes'
    outcome_id = db.Column(db.BigInteger, primary_key=True)
    round_id = db.Column(db.BigInteger, db.ForeignKey('rounds.round_id'))
    outcome_data = db.Column(JSON)
    payout_multiplier = db.Column(NUMERIC)
    round = db.relationship('Round', back_populates='outcome')
    bets = db.relationship('Bet', back_populates='outcome')

class Bet(db.Model):
    __tablename__ = 'bets'
    bet_id = db.Column(db.BigInteger, primary_key=True)
    round_id = db.Column(db.BigInteger, db.ForeignKey('rounds.round_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    amount = db.Column(NUMERIC)
    choice_data = db.Column(JSON)
    placed_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    settled_at = db.Column(db.DateTime(timezone=True))
    outcome_id = db.Column(db.BigInteger, db.ForeignKey('outcomes.outcome_id'))
    payout_amount = db.Column(NUMERIC)
    user = db.relationship('User', back_populates='bets')
    round = db.relationship('Round', back_populates='bets')
    outcome = db.relationship('Outcome', back_populates='bets')

class SarcasTemp(db.Model):
    __tablename__ = 'sarcastemps'
    template_id = db.Column(db.Integer, primary_key=True)
    template_text = db.Column(db.Text)
    severity_level = db.Column(db.SmallInteger)
    user_settings = db.relationship('UserSettings', back_populates='sarcas_template')
