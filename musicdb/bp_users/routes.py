from flask import Blueprint, render_template, url_for, flash, redirect, request
from sqlalchemy import text
from musicdb import app, bcrypt, db
from musicdb.general import p_err
from .forms import RegistrationForm, LoginForm, UpdateAccount, UpdatePicture, UpdateAuth, DeleteAccount
from musicdb.models import User
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user
from werkzeug.utils import secure_filename
from PIL import Image
import hashlib
import uuid
import os

bp_users = Blueprint('users', __name__)

@bp_users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp_users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data, force=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@bp_users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp_users.route('/account', methods=['GET', 'POST'])
def account():

    if not current_user.is_authenticated:
        flash("You shouldn't be on this page without being loged in!")
        return redirect(url_for('users.login'))
    
    updatePicture = UpdatePicture()
    updateAccount = UpdateAccount(name=current_user.name, country_flag=current_user.country, about_me=current_user.about_me)
    updateAuth = UpdateAuth(email=current_user.email, username=current_user.username)
    deleteAccount = DeleteAccount()

    print(f'REQUEST: {request.form}')
    if "current_password" in request.form:
        print('PASS')

    if updateAccount.submit_updateaccount.data and updateAccount.validate_on_submit():
        print('Trigger ACCOUNT')
        current_user.about_me = updateAccount.about_me.data
        current_user.country_flag = updateAccount.country_flag.data
        current_user.name = updateAccount.name.data
        db.session.commit()


    if updateAuth.submit_updateauth.data or updateAuth.validate_on_submit():
        print('Trigger AUTH')
        if bcrypt.check_password_hash(current_user.password, updateAuth.current_password.data):
            current_user.username = updateAuth.username.data
            current_user.email = updateAuth.email.data
            db.session.commit()
            return render_template('account.html', updateAccount=updateAccount, updateAuth=updateAuth, deleteAccount=deleteAccount, updatePicture=updatePicture)

    # Image updating
    if updatePicture.validate_on_submit() and updatePicture.picture.data:
        print('Trigger PICTURE')
        # https://flask-wtf.readthedocs.io/en/latest/form/#module-flask_wtf.file

        # Store the file in tempfolder so we can modify it
        f = updatePicture.picture.data
        filename = secure_filename(f.filename)
        temp = os.path.join(app.config['TEMP_FOLDER'], filename)
        f.save(temp)
        extension = filename.split('.').pop().lower()

        # Crop and resize to 512, 512
        image = Image.open(temp)

        # https://note.nkmk.me/en/python-pillow-square-circle-thumbnail/
        def crop_center(pil_img, crop_width, crop_height):
            img_width, img_height = pil_img.size
            return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))
        
        def crop_max_square(pil_img):
            return crop_center(pil_img, min(pil_img.size), min(pil_img.size))
        
        image_cropped = crop_center(image, 512, 512)


        # image_to_resize = Image.open(temp)
        # icon = image_to_resize.resize((512, 512))
        image_cropped.save(temp)

    
        md5 = hashlib.md5(open(temp, 'rb').read()).hexdigest()

        md5_and_extention = f'{md5}.{extension}'
        persistent = os.path.join(os.path.join(app.config['PROFILE_PICTURE'], md5_and_extention))

        try:
            os.rename(temp, persistent)
        except Exception as e:
            os.remove(temp)
            print(e)

        current_user.profile_picture = md5_and_extention
        db.session.commit()
    return render_template('account.html', updateAccount=updateAccount, updateAuth=updateAuth, deleteAccount=deleteAccount, updatePicture=updatePicture)

@bp_users.route("/profile")
def profile():
    return 'profile'

@bp_users.route("/likes")
def likes():
    query = text('SELECT * FROM view_user_likes_song;')
    answer = db.session.execute(query)

    temp=[]

    for x in answer:
        temp.append(f'{x[0]} likes {x[1]}')

    p_err(temp)

    return render_template('likes.html', likes=temp)