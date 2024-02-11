from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table
from datetime import datetime
from musicdb import login_manager, db
from typing import List


# DO NOT TOUCH. IT WORKS NOW.
# KEEPS EXPLODING WHEN I LOOK AT IT.
@login_manager.user_loader
def load_user(user_id):
    if user_id == '':
        return None
    if User.query.get(int(user_id)) == None:
        return None
    return User.query.get(int(user_id))


class Song(db.Model):
    __tablename__ = 'song'
    # Main DB identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Base information
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="<unknown title>")
    # album (foreign key)
    # artist (foreign key)

    # Metadata
    length_in_sec: Mapped[int] = mapped_column(Integer, default=-1)
    extension: Mapped[str] = mapped_column(String(10), nullable=True)

    # Files
    file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    file_cover: Mapped[str] = mapped_column(String(255), nullable=True)

    # Info about file creation
    # user (aka uploader) (foreign key)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())
    upload_session: Mapped[str] = mapped_column(String(255), nullable=True)
    moved_to_songs: Mapped[bool] = mapped_column(Boolean, default=False)
    alive: Mapped[bool] = mapped_column(Boolean, default=True)


    # RELATIONSHIPS

    # N songs -> 1 uploader
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="song")

    # N songs -> 1 album
    album_id: Mapped[int] = mapped_column(ForeignKey("album.id"), nullable=True)
    album: Mapped["Album"] = relationship(back_populates="song")

    # N songs -> 1 artist
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"), nullable=True)
    artist: Mapped["Artist"] = relationship(back_populates="song")

    # N users -> UsersLikesSongs <- N songs
    liked_users: Mapped[List["UsersLikesSongs"]] = relationship(back_populates="song")

    def __repr__(self):
        return f"Song :: ('{self.id}', '{self.title}', '{self.user}')"
    

class Album(db.Model):
    __tablename__ = 'album'

    # Main DB identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(9999), nullable=True) #blob
    album_cover : Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())

    # 1 album > N songs
    song: Mapped[List["Song"]] = relationship(back_populates="album")

    # N albums -> 1 artist
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"), nullable=True)
    artist: Mapped["Artist"] = relationship(back_populates="album")

    def __repr__(self):
        return f"Album :: ('{self.id}', '{self.artist}')"


class Artist(db.Model):
    __tablename__ = 'artist'

    # Main DB identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(9999), nullable=True) #blob
    country: Mapped[str] = mapped_column(String(255), default='world')
    band_cover : Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())

    # 1 artist -> N songs
    song: Mapped[List["Song"]] = relationship(back_populates="artist")

    # 1 artist -> N albums
    album: Mapped[List["Album"]] = relationship(back_populates="artist")

    def __repr__(self):
        return f"Artist :: ('{self.id}', {self.name}, '{self.country}')"


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    profile_picture: Mapped[str] = mapped_column(String(255), default='default.jpg')
    country: Mapped[str] = mapped_column(String(255), default='world')
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    about_me: Mapped[str] = mapped_column(String(9999), nullable=True) #blob
    password_crypt_method: Mapped[str] = mapped_column(String(255), nullable=False, default='bcrypt')
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    alive: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())

    # 1 user > N songs
    song: Mapped[List["Song"]] = relationship(back_populates="user")
    # N users -> UsersLikesSongs <- N songs
    liked_songs: Mapped[List["UsersLikesSongs"]] = relationship(back_populates="user")


    def __repr__(self):
        return f"User :: ('{self.id}', '{self.username}', '{self.email}')"

    # Is this still required? (we have UserMixin, but right right now I don't wanna break ANYTHING.)
    @property
    def is_authenticated(self):
        return self.is_active
    
class UsersLikesSongs(db.Model):
    __tablename__ = 'users_likes_songs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # User
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="liked_songs")

    # Song
    song_id: Mapped[int] = mapped_column(ForeignKey("song.id"))
    song: Mapped["Song"] = relationship(back_populates="liked_users")

    def __repr__(self):
        return f"LOVE :: ('{self.user}' LIKES '{self.song}')"
