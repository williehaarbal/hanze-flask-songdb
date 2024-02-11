from flask import flash
from markupsafe import Markup
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import FileField, SubmitField, StringField, PasswordField, BooleanField, SelectField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
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

class CreateArtist(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('description', validators=[Length(min=0, max=9999)])
    country_flag = SelectField(label='Country', choices=([country for country in countries]), validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Create')
    
    def validate_name(self, name):
        excist = db.session.query(Artist.id, Artist.name).filter(func.lower(Artist.name) == func.lower(name.data)).first() is not None
        if excist:

            id, name = db.session.query(Artist.id, Artist.name).filter(func.lower(Artist.name) == func.lower(name.data)).first()
           
            raise ValidationError(Markup(f"<b>Band with name {name} already exists!<b>"))


class html_container():
    x = None
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return str(self.x)