from app import db
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from bcrypt import gensalt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = PasswordHasher().hash(password)

    def check_password(self, password):
        try:
            x = PasswordHasher().verify(self.password_hash, password)
        except VerifyMismatchError:
            x = False
        return x


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sum = db.Column(db.Integer)
    recipent_account = db.Column(db.String(32))
    recipent_name = db.Column(db.String(120))

    def __init__(self, user_id, sum, account, name):
        self.user_id = user_id
        self.sum = sum
        self.recipent_account = account
        self.recipent_name = name


class Forgot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String(120))

    def __init__(self, user_id, code):
        self.user_id = user_id
        self.code = code

@login.user_loader
def load_user(id):
    return User.query.get(int(id))