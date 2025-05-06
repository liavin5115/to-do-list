from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from datetime import datetime
from enum import Enum
from pytz import UTC, timezone

class BoardPermission(Enum):
    VIEW = 'view'
    EDIT = 'edit'
    MANAGE = 'manage'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # Add relationship to boards
    boards = db.relationship('Board', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Update the board_members table
board_members = db.Table('board_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('board_id', db.Integer, db.ForeignKey('board.id'), primary_key=True),
    db.Column('permission', db.Enum(BoardPermission), default=BoardPermission.VIEW)
)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    # Relationship to lists
    lists = db.relationship('List', backref='board', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('User', 
                            secondary=board_members,
                            lazy='dynamic',
                            backref=db.backref('shared_boards', lazy='dynamic'))

    def __repr__(self):
        return f'<Board {self.name}>'

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign key to Board
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    # Relationship to cards
    cards = db.relationship('Card', backref='list', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<List {self.name}>'

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    # Foreign key to List
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    # Relationship to comments
    comments = db.relationship('Comment', backref='card', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < datetime.utcnow()
        return False

    def __repr__(self):
        return f'<Card {self.title}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    user = db.relationship('User', backref='comments')

    def formatted_date(self):
        """Convert UTC time to local time and format it"""
        local_tz = timezone('Asia/Jakarta')  # Change this to your timezone
        local_dt = self.created_at.replace(tzinfo=UTC).astimezone(local_tz)
        return local_dt.strftime('%d %b %Y, %H:%M')

    def __repr__(self):
        return f'<Comment {self.id}>'