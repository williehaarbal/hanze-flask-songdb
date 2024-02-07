from app import login_manager
from flask_login import UserMixin
from app.db_handler import DB
from app.sql.sql import *
from flask_login import login_user, current_user
import inspect


@login_manager.user_loader
def load_user(user_static_id):
    print('IS THIS SHIT BEIG CALLED?!')
    print(inspect.getouterframes( inspect.currentframe() )[1])
    print(user_static_id)
    # print(type(static_user_id))
    

    if user_static_id == 'None':
        return None
    return User(user_static_id)

# @login_manager.user_loader
# def load_user(static_user_id):
#     # print('IS THIS SHIT BEIG CALLED?!')
#     # print(static_user_id)
#     # print(type(static_user_id))
    

#     if static_user_id == 'None':
#         return None
#     return User(static_user_id)


class User():
    id = None
    name = None
    username = None
    email = None
    confirmed_email = None
    loc_profile_pic = None
    country_flag = None
    created_at = None

    users_list = []

    def __init__(self, user_static_id: str) -> None:
        super().__init__()
        # print('CREATING CURRENT USER')
        self.user_static_id = user_static_id

        
        db = DB('main.db')
        db.exe(SQL_GET_MOST_BY_USER_STATIC_ID(self.user_static_id))
        
        # print("WORDT HIER IETS GERAAKT")
        answer = db.f_all()
        # print(answer)
        # print("WORDT HIER IETS GERAAKT")
        try:

            print(f'Deze {answer}')

            (name,
            username,
            email,
            confirmed_email,
            loc_profile_pic,
            country_flag,
            created_at,
            id) = answer[0] # used to be static id

            self.name = name
            self.username = username
            self.email = email
            self.confirmed_email = confirmed_email
            self.loc_profile_pic = loc_profile_pic
            self.country_flag = country_flag
            self.created_at = created_at


            self.users_list.append(self)
            # print('DUMP')
            # print(self.user_static_id)
            # print(self.name)
            # print(self.username)
            # print(self.email)
            # print(self.loc_profile_pic)
            # print(self.country_flag)
            # print(self.created_at)
            # print(self.confirmed_email)


        except:
            print('Er word None geretourneerd')
            answer = None
        finally:
            db.close()

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id
        # return super().get_id()

    def get_user(self, x):
        return [user for user in self.users_list if user.user_static_id == x]
    
    __hash__ = object.__hash__

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal