from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, NUMERIC
from sqlalchemy import ForeignKey
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    pw_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    profile_picture = db.Column(db.String(255), default='default_profile.png')
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)
    wallets = db.relationship('Wallet', back_populates='user')
    bets = db.relationship('Bet', back_populates='user')

    def get_id(self):
        return str(self.user_id)

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


# Horse Racing specific models
class Horse(db.Model):
    __tablename__ = 'horses'
    horse_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    age = db.Column(db.SmallInteger, db.CheckConstraint('age BETWEEN 2 AND 15'), nullable=False)
    base_speed = db.Column(NUMERIC(4,1), db.CheckConstraint('base_speed > 0'), nullable=False)
    temperament = db.Column(db.String(20), nullable=False)
    
    # Relationships
    runners = db.relationship('HorseRunner', back_populates='horse')


class HorseRunner(db.Model):
    __tablename__ = 'horse_runners'
    round_id = db.Column(db.BigInteger, db.ForeignKey('rounds.round_id', ondelete='CASCADE'), primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.horse_id'), primary_key=True)
    lane_no = db.Column(db.SmallInteger, db.CheckConstraint('lane_no BETWEEN 1 AND 6'), nullable=False)
    odds = db.Column(NUMERIC(6,3), nullable=False)
    
    # Relationships
    round = db.relationship('Round', backref='horse_runners')
    horse = db.relationship('Horse', back_populates='runners')
    result = db.relationship('HorseResult', back_populates='runner', uselist=False)


class HorseResult(db.Model):
    __tablename__ = 'horse_results'
    round_id = db.Column(db.BigInteger, primary_key=True)
    horse_id = db.Column(db.Integer, primary_key=True)
    lane_no = db.Column(db.SmallInteger, nullable=False)
    finish_place = db.Column(db.SmallInteger, db.CheckConstraint('finish_place BETWEEN 1 AND 6'), nullable=False)
    race_time_sec = db.Column(NUMERIC(6,3), nullable=False)
    
    # Composite foreign key
    __table_args__ = (
        db.ForeignKeyConstraint(['round_id', 'horse_id'], ['horse_runners.round_id', 'horse_runners.horse_id']),
        db.ForeignKeyConstraint(['horse_id'], ['horses.horse_id']),
    )
    
    # Relationships
    runner = db.relationship('HorseRunner', back_populates='result')
    horse = db.relationship('Horse', primaryjoin='HorseResult.horse_id == Horse.horse_id')
