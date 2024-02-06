from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField, StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed
from werkzeug.utils import secure_filename
from app.sql.sql import *
from app.db_handler import DB
import eyed3
import sqlite3
import uuid
import os



class UploadFileForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload fie")

# TODO: More countries?
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

    def validate_username(self, username):
        db = DB()
        db.exe(SQL_USERNAME_EXISTS(username.data))
        answer = db.fall()[0][0]
        db.close()
        if answer == 'True':
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        db = DB()
        db.exe(SQL_CONFIRMED_EMAIL_EXISTS(email.data))
        answer = db.fall()[0][0]
        db.close()
        if answer == 'True':
            raise ValidationError('That email is taken. Please choose a different one.')
    
    def validate_country_flag(self, country_flag):
        if country_flag.data == 'Please select country':
            raise ValidationError('Please select a country')

  
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')