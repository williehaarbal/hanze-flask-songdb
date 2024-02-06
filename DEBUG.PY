
from app.sql.sql import *

from app.models import User

usertest = User('test')

print(usertest.static_user_id)
print(usertest.name)
print(usertest.username)
print(usertest.email)
print(usertest.loc_profile_pic)
print(usertest.country_flag)
print(usertest.created_at)
print(usertest.confirmed_email)