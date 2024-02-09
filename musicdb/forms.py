# TODO: More countries?

from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField, StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from flask_wtf.file import FileAllowed
from wtforms.widgets import TextArea


countries = ('Please select country', 'Nederland', 'Duitsland', 'Belgie', 'Other')

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    country_flag = SelectField(label='Country', choices=([country for country in countries]), validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    stay_signed_in = BooleanField(label='Stay signed in')
    submit = SubmitField('Sign Up')

class UpdatePicture(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    # submit_picture = SubmitField('picture')

class UpdateAccount(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=20)])
    country_flag = SelectField(label='Country', choices=([country for country in countries]), validators=[DataRequired()])
    about_me = TextAreaField('About me', widget=TextArea())
    submit_updateaccount = SubmitField('Update')

class UpdateAuth(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('new password', validators=[])
    confirm_password = PasswordField('confirm Password', validators=[EqualTo('password')])
    current_password = PasswordField('current password', validators=[])
    submit_updateauth = SubmitField('Update')

class DeleteAccount(FlaskForm):
    password = PasswordField('Password', validators=[])
    delete = StringField('delete', validators=[])
    submit_deleteaccount = SubmitField('delete')

# class DeleteAccount(FlaskForm):
#     password = PasswordField('Password', validators=[DataRequired()])
#     delete = StringField('delete', validators=[DataRequired(), Length(min=6, max=6)])
#     submit_deleteaccount = SubmitField('delete')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload file")

