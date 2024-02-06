from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from app.sql.sql import *
import eyed3
import sqlite3
import uuid
import pathlib
import os

from app.forms import *
from app.db_handler import DB

from app import app


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
def upload():
    
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
    form = LoginForm()
    return render_template('login.html', title='login', form=form)



@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    form = RegistrationForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():

        db = DB()

        # Username
        wanted_username = form.username.data
        db.exe(SQL_USERNAME_EXISTS(wanted_username))
        answer = db.fall()[0][0]
        if answer == "True":
            error.append('Username already in use!')
            print('Username already in use!')
        
        # Email
        wanted_email = form.email.data
        db.exe(SQL_CONFIRMED_EMAIL_EXISTS(wanted_email))
        answer = db.fall()[0][0]
        if answer == "True":
            error.append('Email already in use!')

        confirmed_email = 'False'
        
        # Password
        print(f"HASHED {form.password.data}")
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        crypt_method = 'bcrypt 1.0.1'

        # User_statid_id
        db.exe(SQL_GET_HIGHEST_USER_ID())
        answer = db.fall()[0][0]
        real_number = int(answer)
        user_static_id = real_number + 1

        # Name
        wanted_name = form.name.data

        # Country flag
        wanted_country_flag = form.country_flag.data

        # Image
        loc_profile_pic = 'default.png'

        # Admin
        admin = 'False'


        db.exe(SQL_INSERT_NEW_USER(user_static_id, wanted_name, wanted_username, hashed_password, crypt_method, wanted_email, confirmed_email, loc_profile_pic, wanted_country_flag, 'False', 'True'))
        db.commit()
        db.close()
        print('Tried adding user')
        return redirect('/',code=302)


    print('loading register page')
    return render_template('register.html', title='Register', form=form)


@app.route("/", methods=['get'])
def home():
    return "home"