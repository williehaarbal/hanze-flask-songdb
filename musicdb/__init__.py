from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os

class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

root_folder = os.getcwd()

# DEBUG
print(os.path.join(root_folder, 'database', 'main.db'))

# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////{os.path.join(root_folder, 'database', 'main.db')}"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///main.db"
app.config['DATA_FOLDER'] = os.path.join(os.getcwd(), 'data')
app.config['TEMP_FOLDER'] = os.path.join(os.getcwd(), 'data', 'temp')
app.config['SONG_FOLDER'] = os.path.join(os.getcwd(), 'data', 'songs')
app.config['SONG_COVERS_ICON'] = os.path.join(os.getcwd(), 'data', 'songs_covers_icon')
app.config['PROFILE_PICTURE'] = os.path.join(os.getcwd(), 'data', 'profile_pictures')
app.config['BAND_COVER'] = os.path.join(os.getcwd(), 'data', 'band_covers')

db = SQLAlchemy(model_class=Base)
db.init_app(app)

DEBUG = True

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'bp_users.login'
login_manager.login_message_category = 'info'


from musicdb.bp_users.routes import bp_users
from musicdb.bp_songs.routes import bp_songs
from musicdb.bp_utils.routes import bp_utils
from musicdb.bp_main.routes import bp_main
from musicdb.bp_artists.routes import bp_artists

app.register_blueprint(bp_users)
app.register_blueprint(bp_songs)
app.register_blueprint(bp_main)
app.register_blueprint(bp_utils)
app.register_blueprint(bp_artists)