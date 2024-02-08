from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from musicdb import login_manager, db


@login_manager.user_loader
def load_user(user_id):
    print(f'HELP: {user_id}')
    if user_id is '':
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
    password_crypt_method: Mapped[str] = mapped_column(String(50), nullable=False, default='bcrypt')
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    admin: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"User :: ('{self.static_id}' '{self.username}', '{self.email}')"

    @property
    def is_authenticated(self):
        return self.is_active