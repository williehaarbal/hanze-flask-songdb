from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from flask_login import UserMixin
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from musicdb import login_manager, db
from typing import List

@login_manager.user_loader
def load_user(user_id):
    if user_id == '':
        return None
    if User.query.get(int(user_id)) == None:
        return None
    return User.query.get(int(user_id))

# Backup this works kinda
# @login_manager.user_loader
# def load_user(user_id):
#     print(f'HELP: {user_id}')
#     if user_id is '':
#         return None
#     if User.query.get(int(user_id)) == None:
#         return None
#     return User.query.get(int(user_id))




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    static_id: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_picture: Mapped[str] = mapped_column(String(100), default='default.jpg')
    country: Mapped[str] = mapped_column(String(20), default='world')
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    about_me: Mapped[str] = mapped_column(String(2000), nullable=True)
    password_crypt_method: Mapped[str] = mapped_column(String(50), nullable=False, default='bcrypt')
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    alive: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())

    # songs: Mapped[List["Song"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User :: ('{self.static_id}' '{self.username}', '{self.email}')"

    @property
    def is_authenticated(self):
        return self.is_active
    

    
class Song(db.Model):
    __tablename__ = 'Songs'
    # Main DB identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    static_id: Mapped[int] = mapped_column(Integer, default=0)

    # Base information
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    artist: Mapped[str] = mapped_column(String(100), nullable=True)
    album: Mapped[str] = mapped_column(String(100), nullable=True)

    # Meta data
    length_in_sec: Mapped[int] = mapped_column(Integer, default=-1)
    extension: Mapped[str] = mapped_column(String(10), nullable=True)

    # Files
    # Stores name of the file+ext of where to find the uploaded file ondisk (data/songs)
    file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    # Stores name if the file+ext of where a short clip can be found of the original file (data/shorts)
    file_shorts: Mapped[str] = mapped_column(String(255), nullable=True)
    # Stores the BIG/ORIG image of the orignal file, if it had any. Is md5+ext (data/songs_covers)
    # Also a small icon will be available in (data/songs_covers_icon) (128x128)
    file_cover: Mapped[str] = mapped_column(String(255), nullable=True)

    # Info about file creation
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())
    upload_session: Mapped[str] = mapped_column(String(255), nullable=True)
    moved_to_songs: Mapped[bool] = mapped_column(Boolean, default=False)
    alive: Mapped[bool] = mapped_column(Boolean, default=True)

    uploader: Mapped[str] = mapped_column(String(100), nullable=True)

    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user: Mapped["User"] = relationship(back_populates="songs")

    def __repr__(self):
        return f"Song :: ('{self.static_id}' '{self.title}', '{self.uploader}')"