from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from app.sql.sql import *
import eyed3
import sqlite3
import uuid
import pathlib
import os



app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'SuperSecretKey'
app.config['PERSISTENT_FOLDER'] = 'files'
app.config['TEMP_FOLDER'] = 'temp'
app.config['ALBUM_COVERS'] = 'album_covers'
app.config['ROOT_FOLDER'] = os.getcwd() #Where is run.py?
app.config['DATABASE_FILE'] = 'database/main.db'
bcrypt = Bcrypt(app)


from app.forms import *
from app.db_handler import DB
from app.routes import *