from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin, LoginManager
from app.sql.sql import *
import os


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'rg5;@zvlG50WEnw9N=rhrN#c#'
app.config['PERSISTENT_FOLDER'] = 'files'
app.config['TEMP_FOLDER'] = 'temp'
app.config['ALBUM_COVERS'] = 'album_covers'
app.config['ROOT_FOLDER'] = os.getcwd() #Where is run.py?
app.config['DATABASE_FILE'] = 'database/main.db'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app=app)
login_manager.session_protection = None

# class AnomUser(AnonymousUserMixin):
#     user_static_id = 0

#     def __init__(self) -> None:
#         super().__init__()

#     def get_id(self):
#         return str(0)
    
#     def __call__(self):
#         return self
    
#     @property
#     def is_authenticated(self):
#         return False

#     @property
#     def is_active(self):
#         return False

#     @property
#     def is_anonymous(self):
#         return True

#     def get_id(self):
#         return

# login_manager.anonymous_user = AnomUser()

from app.forms import *
from app.routes import *
from app.routes_register import *
from app.routes_login import *