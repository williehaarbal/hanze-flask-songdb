from flask import flash
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import FileField, SubmitField, StringField, PasswordField, BooleanField, SelectField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed
from wtforms.widgets import TextArea
from musicdb import db
from musicdb.models import Artist

from musicdb.models import Artist


countries = {
    'Netherlands': 'nl.svg',
    'Germany': 'ge.svg'
}

class CreateArtist(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('description', validators=[Length(min=0, max=9999)])
    country_flag = SelectField(label='Country', choices=([country for country in countries]), validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Create')
    
    def validate_name(self, name):
        excist = db.session.query(Artist.id).filter_by(name = name.data).first() is not None
        if excist:
            raise ValidationError('Band already registered! No need to add it once more.')




   # def validate_username(self, username):
    #     db = DB()
    #     db.exe(SQL_USERNAME_EXISTS(username.data))
    #     answer = db.fall()[0][0]
    #     db.close()
    #     if answer == 'True':
    #         raise ValidationError('That username is taken. Please choose a different one.')

    # def validate_email(self, email):
    #     db = DB()
    #     db.exe(SQL_CONFIRMED_EMAIL_EXISTS(email.data))
    #     answer = db.fall()[0][0]
    #     db.close()
    #     if answer == 'True':
    #         raise ValidationError('That email is taken. Please choose a different one.')