from init import db
from utils import generate_salt, generate_token


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(256), unique=True)
    pwdhash = db.Column(db.String(256))

    def __init__(self, email=None, pwdhash=None, salt=None):
        self.email = email
        self.pwdhash = pwdhash + salt


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(256), unique=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, email=None):
        u = User.query.filter_by(email=email).first()
        if u is None:
            return
        self.id_user = u.id
        self.token = unicode(generate_token())


class Salt(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salt = db.Column(db.String(132), unique=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, email=None, salt=None, id_user=None):
        if id_user is None:
            u = User.query.filter_by(email=email).first()
            if u is None:
                return
            self.id_user = u.id
        else:
            self.id_user = id_user
        self.salt = salt

class EmailToken(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(132), unique=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    enable = db.Column(db.Boolean)

    def __init__(self, email=None):
        u = User.query.filter_by(email=email).first()
        if u is None:
            return
        self.id_user = u.id
        self.enable = False
        self.token = unicode(generate_token())


