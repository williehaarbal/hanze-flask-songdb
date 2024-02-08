# TODO: More countries?

from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField, StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from flask_wtf.file import FileAllowed



countries = ('Please select country', 'Nederland', 'Duitsland', 'Belgie', 'Other')

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=4, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    country_flag = SelectField(label='Country', choices=([country for country in countries]), validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    stay_signed_in = BooleanField(label='Stay signed in')
    submit = SubmitField('Sign Up')
  
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload file")

