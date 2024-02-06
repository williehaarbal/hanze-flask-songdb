from app import login_manager
from flask_login import UserMixin
from app.db_handler import DB
from app.sql.sql import *
from flask_login import login_user, current_user


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class User(UserMixin):

    def __init__(self, id, name):
        print('making new user')
        self.id = id
        self.name = name
        self.some_text = "I am a happy user"

    def get(self):
        return self


# class User(UserMixin):
#     id = None
#     name = None
#     username = None
#     email = None
#     confirmed_email = None
#     loc_profile_pic = None
#     country_flag = None
#     created_at = None

#     def __init__(self, username: str) -> None:
#         super().__init__()
#         # print('CREATING CURRENT USER')
#         self.username = username

#         db = DB()
#         db.exe(SQL_GET_MOST_BY_USERNAME(self.username))

#         answer = db.fall()[0]
        

#         (self.name,
#         self.email,
#         self.confirmed_email,
#         self.loc_profile_pic,
#         self.country_flag,
#         self.created_at,
#         self.id) = answer # used to be static id


#         # print(self.static_user_id)
#         # print(self.name)
#         # print(self.username)
#         # print(self.email)
#         # print(self.loc_profile_pic)
#         # print(self.country_flag)
#         # print(self.created_at)
#         # print(self.confirmed_email)

#         db.close()

#     def get_id(self):
#         return self.id
#         # return super().get_id()