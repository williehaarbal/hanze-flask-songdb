from flask import flash
from markupsafe import Markup
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import FileField, MultipleFileField, SubmitField, StringField, PasswordField, BooleanField, SelectField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from flask_wtf.file import FileAllowed
from wtforms.widgets import TextArea
from musicdb import db
from musicdb.models import Artist
from bs4 import BeautifulSoup
from musicdb.models import Artist

countries = {
    'Netherlands': 'nl',
    'Germany': 'de',
    'United Kingdom': 'gb',
    'Sweden': 'se',
    'Poland': 'pl',
    'Belgium': 'be',
    'USA': 'us',
    'France': 'fr',
    'Other': None
}

class UploadForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload file")


class IgnoreVal(InputRequired):
    field_flags = ()

class UpdateSong(FlaskForm):
    # MULTI LEVEL PYRAMID FORM
    # (COMBINES SONGS, ARTISTT AND ALBUMS!)

    # Song
    title = StringField(label='title', validators=[Length(min=1, max=200)])
    artist = SelectField(label='artist', choices=(), coerce=str, validators=[])
    album = SelectField(label='album', choices=(), coerce=str, validators=[])
    alive = SelectField(label='alive', choices=(), coerce=str, validators=[])

    submit = SubmitField('Create')


