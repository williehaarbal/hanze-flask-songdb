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

class IgnoreVal(InputRequired):
    field_flags = ()

class UpdateAlbum(FlaskForm):
    # MULTI LEVEL PYRAMID FORM
    # (COMBINES SONGS, ARTISTT AND ALBUMS!)

    # Song
    name = StringField(label='name', validators=[Length(min=1, max=200)])
    artist = SelectField(label='artist', choices=(), coerce=str, validators=[])
    description = TextAreaField(label='Sumary')

    submit = SubmitField('UPDATE')