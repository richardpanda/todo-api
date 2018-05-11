import jwt

from app import db
from bcrypt import checkpw, gensalt, hashpw
from flask import current_app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    hash = db.Column(db.String(60))

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
