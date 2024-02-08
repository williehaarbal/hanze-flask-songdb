from flask_login import UserMixin
from datetime import datetime

from itsdangerous import Serializer
from musicdb import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    static_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(26), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    pic_profile = db.Column(db.String(20), nullable=False, default='default.jpg')
    country = db.Column(db.String(26), nullable=False, default='world')
    password = db.Column(db.String(255), nullable=False)
    password_crypt_method = db.Column(db.String(26), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    # RELATIONSHIPS
    Songs = db.relationship('Songs', backref='uploader', lazy=True)

    def __repr__(self):
        return f"User :: ('{self.static_id}' '{self.username}', '{self.email}')"

class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    static_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Song :: ('{self.static_id}' '{self.title}', '{self.artist}')"
    
class Artists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    static_id = db.Column(db.Integer, unique=True, nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Artist :: ('{self.static_id}' '{self.name}')"

class Albums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    static_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    album_cover = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Album :: ('{self.static_id}' '{self.name}', '{self.artist}')"