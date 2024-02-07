from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_login import login_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from app.sql.sql import *
import random
from app.color import bcol
import eyed3
import logging
import sqlite3
import time
import uuid
import pathlib
import os

from app.models import User
from app.forms import *
from app.db_handler import DB
from app import app
from app import bcrypt



@app.route("/register", methods=['GET', 'POST'])
def register():
    # For each page
    error = None
    title = 'MusicDB :: Sign up'

    form = RegistrationForm()

    if form.validate_on_submit():

        try:
            # Open database connection.
            db = DB('main.db')

            # Check if username is available, else raise expection
            wanted_username = form.username.data
            db.exe(SQL_USERNAME_EXISTS(wanted_username))
            answer = db.f_one_untuppled()
            
            # Already exists?
            if answer == "True":
                raise Exception(f"{bcol.FAIL}REGISTER ERROR: A user already exists with username '{wanted_username}'! {bcol.END}")
            
            # Check if email is available
            wanted_email = form.email.data
            db.exe(SQL_EMAIL_EXISTS(wanted_email))
            answer = db.f_one_untuppled()

            # Already exists?
            if answer == "True":
                raise Exception(f"{bcol.FAIL}REGISTER ERROR: Email '{wanted_email}' is already taken! {bcol.END}")
            
            # Hash password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            crypt_method = 'bcrypt 1.0.1'

            # Get a random user_static_id (main way to identify users)
            while(True):
                random_number = random.randint(100000, 999999)
                random_number = str(random_number)
                db.exe(SQL_USER_STATIC_ID_EXISTS(random_number))
                answer = db.f_one_untuppled()
                if answer == 'True':
                    continue
                else:
                    user_static_id = random_number
                    break

            # Other things   
            wanted_country_flag = form.country_flag.data
            loc_profile_pic = 'default.png'
            admin = 'False'
            wanted_name = form.name.data
            confirmed_email = 'False'
                
            print(SQL_INSERT_NEW_USER(user_static_id, wanted_name, wanted_username, hashed_password, crypt_method, wanted_email, confirmed_email, loc_profile_pic, wanted_country_flag, 'False', 'True'))
            db.exe(SQL_INSERT_NEW_USER(user_static_id, wanted_name, wanted_username, hashed_password, crypt_method, wanted_email, confirmed_email, loc_profile_pic, wanted_country_flag, 'False', 'True'))
            
            db.commit()
            flash(f'Account created! Username: {wanted_username}')

            

            
            return redirect(url_for('home'), code=302)
            
        
        except Exception as e:
            print(e)
        finally:
            db.close()
        

    return render_template('register.html', title=title, error=error, form=form)