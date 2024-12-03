# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Enum, ForeignKey
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from datetime import datetime

from apps import db, login_manager
from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.LargeBinary)
    role = db.Column(Enum('admin', 'editor', 'viewer', 'demo'), default='viewer', nullable=False, server_default='viewer')
    oauth_github  = db.Column(db.String(100), nullable=True)

    # Relationships
    reminders = relationship('Reminder', back_populates='user', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            if property == 'password':
                value = hash_pass(value)
            setattr(self, property, value)

    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}>"
    
    def is_admin(self):
        return self.role == 'admin'

    def is_editor(self):
        return self.role == 'editor'


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)


class Reminder(db.Model):
    __tablename__ = 'Reminders'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    reminder_time = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, ForeignKey('Users.id'), nullable=False)

    # Relationships
    user = relationship('Users', back_populates='reminders')

    def __repr__(self):
        return f"<Reminder {self.email} - {self.message} at {self.reminder_time}>"
