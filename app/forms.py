from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed
from werkzeug.utils import secure_filename
from app.sql.sql import *
import eyed3
import sqlite3
import uuid
import os



class UploadFileForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload fie")


class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=4, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')