from app import db
from bcrypt import gensalt, hashpw


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(60))

    def __init__(self, username, password):
        self.username = username
        self.password = hashpw(password.encode(), gensalt()).decode()

    def __repr__(self):
        return f'<User id={self.id} username={self.username} password={self.password}>'
