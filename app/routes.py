from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_login import login_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import flask_login
from app.sql.sql import *
import eyed3
import logging
import time
import sqlite3
import uuid
import pathlib
import os

from app.models import User
from app.forms import *
from app.db_handler import DB
from app import app
from app import bcrypt

# Fontpage of website
@app.route('/')
def home():
     # For each page
    title = 'MusicDB :: home'
    error = None


    # flash('You were successfully logged in')
    # flash('You were successfully logged in')
    # flash('You were successfully logged in')
    # flash('You were successfully logged in')


    print(f'What is user_login in home {current_user}')
    # print(current_user.is_authenticated)
    # print(current_user.user_static_id)
    # print(current_user.name)
    # print(error)
    # print(title)

    return render_template('home.html', title=title, error=error)

@app.route('/test')
def test():
     # For each page
    title = 'MusicDB :: home'
    error = None
    return 'hi'


@app.route('/logout')
def logout():
     # For each page
    title = 'MusicDB :: Logout'
    time.sleep(2)
    error = None
    flask_login.logout_user()

    return redirect(url_for('login'))








@app.route('/upload/<session>')
def upload_session(session):

    db = DB()
    db.exe(SQL_GET_SONGS_BY_UPLOAD_SESSION(session))
    answer = db.fall()

    return render_template('upload_session.html', us=session, rows=answer)


@app.route('/upload/<session>', methods=["POST"])
def update_upload_session(session):
    if request.method == 'POST':
        print(request.form)
        
        answer = request.form.to_dict()

        
        print(answer)
        print(type(answer))

        db = DB()

        for i in answer:
            key = i
            id = key.split('-')[0]
            id = int(id)
            print(id)
            value = answer[i]
        
            db.exe(SQL_CHANGE_ELEMENT_BY_ID(id, 'song_name', value))

        # {'13-song': 'Baby Drumawdawdmer', '14-song': 'Bored of Badawdabies'}
        db.commit()
        db.close()
        return ('', 204)
    





@app.route('/upload', methods=['GET', 'POST'])
def upload(session):
    
    upload_form = UploadFileForm()
    if upload_form.validate_on_submit():

        # Once the user has selected and pressed the upload button the next happens:
        # For each file:
        # TODO: Make sure these song_id's are unique
        # 1. We get a random truncated uuid (This will be its unique identifier / song_ID)
        # 1. We check if the filename is safe, and get the filename
        # TODO: figure out how it happens, all at once, or one at a time
        # 1. We upload it to temp under the [uuid]_safe_orig_filename 

        # 2. We get the info:
        # - The uuid (64 bit)
        # - title,
        # - artist,
        # - album,
        # - type,

        # - (maybe)
        # - album/song/cover
        # - duration

        # 3. We got the file in temp, we got data
        # We now add a db entry that we got it
        
        # 4. We move the file from temp -> files
        # 5. We mark confirmed in files


        # Create a database connector for this upload session. If there are multiple connections from different sessions, this shouldn't be an issue.
        db = DB()

        # We currently accept mp3
        # TODO: add support for others, including JPEG and PNG (for album covers)
        uploaded_files = []

        # Get an upload session ID. This can get used to find all the files uploaded and redirect to those. Also errorchecking!
        upload_session_uuid = uuid.uuid4().int>>64 # Convert 128-bit UUID to 64, good enough for production and use in SQLTE, when using different database, use 128BIT UUID

        for file in upload_form.files.data:
            # TODO: Make this bigger? Or unique?
            song_uuid = uuid.uuid4().int>>32
            save_file_name = secure_filename(file.filename)
            extension = pathlib.Path(save_file_name).suffix # What if no extension? Shouldnt really happen anyway
            uuid_filename = f"[{song_uuid}]{save_file_name}"
            absolute_path_and_file = os.path.join(app.config['TEMP_FOLDER'], uuid_filename)
            file.save(absolute_path_and_file)

            uploaded_files.append(uuid_filename)
            # File should now be stored on server in temp
            # GET METADATA

            meta_file = eyed3.load(absolute_path_and_file)
            meta_title = meta_file.tag.title
            meta_artist = meta_file.tag.artist
            meta_album = meta_file.tag.album
            meta_image = None
            for image in meta_file.tag.images:
                image_uuid = uuid.uuid4().int>>32
                image_file = open(os.path.join(os.path.join(app.config['ROOT_FOLDER'], app.config['ALBUM_COVERS']), f'{image_uuid}.png'), 'wb')
                image_file.write(image.image_data)
                image_file.close()
                break
            meta_image = image_uuid
            meta_duration = meta_file.info.time_secs

            # Got all meta data, now add the entry to database

            db.exe(SQL_INSERT_INTO_SONG(meta_title, meta_artist, meta_album, extension, meta_duration, image_uuid, uuid_filename, upload_session_uuid))
            db.commit()
        # Done with adding all songs to DB!
            
        # We move all temp songs to files
        for file in uploaded_files:
            temp = os.path.join(os.path.join(app.config['ROOT_FOLDER'], app.config['TEMP_FOLDER']), file)
            print(f"Temp file: {temp}")
            files = os.path.join(os.path.join(app.config['ROOT_FOLDER'], app.config['PERSISTENT_FOLDER']), file)
            print(f"Persistent file: {files}")
            os.rename(temp, files)
        
        db.close()

        print("THIS SHIT FUCKING WORKS")

        # Go to a page with sesion UUID, so we can see all the songs just uploaded!
        return redirect(url_for('upload_session', session=upload_session_uuid))
    
    return render_template('upload.html', form=upload_form)



# ROUTE WITH ALL SONGS






@app.route("/login", methods=['GET', 'POST'])
def login():
    # For each page
    error = None
    title = 'MusicDB :: Sign In'


    form = LoginForm()

    if form.validate_on_submit():
        used_email = form.email.data
        used_pw = form.password.data
        username = None

        # We get the hashed password for that email
        db = DB('main.db')
        db.exe(SQL_GET_PASSWORD_HASH_FOR_EMAIL(used_email))
        hashed_password = db.f_all()[0][0]
        db.close()

        if (bcrypt.check_password_hash(hashed_password, used_pw)):
            print('Right password!')


            db = DB('main.db')
            db.exe(SQL_GET_USER_STATIC_ID_FOR_EMAIL(used_email))
            user_static_id = db.f_all()[0][0]
            print(user_static_id)

            current = User(str(user_static_id))

            # WHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHYYYYY
            login_user(current, force=True, remember=True)

            print(f'Object current User: {current_user}')
            print(f'name current User: {current_user.name}')
            print(f'static_user_id current User: {current_user.user_static_id}')

            print(f'Net na login_user {login_user}')
            print(type(current))
            
            #validate redirect
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('home'))
        else:
            print('Wrong password!')

        flash('Login')
            
        

    return render_template('login.html', title='login', form=form)