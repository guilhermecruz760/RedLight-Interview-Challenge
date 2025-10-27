from . import db
from flask_login import UserMixin
from sqlalchemy import Enum

event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(200), nullable = False)
    role = db.Column(Enum('participant', 'admin', name = 'user_roles'), default = "participant", nullable = False)

    age = db.Column(db.Integer, nullable = True)
    photo = db.Column(db.String(200), nullable = True) #path to Photo

    events_created = db.relationship('Event', backref='creator', lazy=True)
    events_joined = db.relationship('Event', secondary=event_participants, backref='participants')

    photo = db.Column(db.String(120), nullable=True)

class Event (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100), nullable = False)
    datetime = db.Column(db.DateTime, nullable = False)
    sport_type=db.Column(db.String(50), nullable = False)
    max_participants = db.Column(db.Integer, nullable = False)
    status = db.Column(Enum('planned','completed', 'cancelled', name = 'event_status'), default = 'planned', nullable = False)
    deleted = db.Column(db.Boolean, default = False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    photos = db.Column(db.Text)
