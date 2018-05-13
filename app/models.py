import jwt

from app import db
from bcrypt import checkpw, gensalt, hashpw
from flask import current_app
from sqlalchemy.orm import relationship


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Todo id={self.id} text={self.text} is_completed={self.is_completed} user_id={self.user_id}>'

    def as_dict(self):
        return {'id': self.id, 'text': self.text, 'is_completed': self.is_completed}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    hash = db.Column(db.String(60))
    todos = relationship('Todo', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.hash = hashpw(password.encode(), gensalt()).decode()

    def __repr__(self):
        return f'<User id={self.id} username={self.username} hash={self.hash}>'

    def check_password(self, password):
        return checkpw(password.encode(), self.hash.encode())

    def generate_jwt(self):
        return jwt.encode({'id': self.id}, current_app.config['JWT_SECRET'], algorithm='HS256').decode()
