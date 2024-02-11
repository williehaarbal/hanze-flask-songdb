import math
from sqlalchemy import func
from werkzeug.utils import secure_filename
from musicdb.bp_artists.routes import create_artist, parse_artist_url
from musicdb.models import Artist, Song
from flask_login import current_user
from musicdb import app, db
from musicdb.general import p_err, p_note
from flask import Blueprint, flash, redirect, render_template, url_for
from .forms import UploadForm
from PIL import Image
import hashlib
import eyed3
import uuid
import os

bp_songs = Blueprint('songs', __name__)

############################################################
# Route for uploading songs
# TODO BASICS, rewrite, split responsibilities
############################################################
@bp_songs.route('/upload', methods=['GET', 'POST'])
def upload():

    if not current_user.is_authenticated:
        flash('Please login to start uploading.')
        return redirect(url_for('bp_songs.login'))
    
    form = UploadForm()
    if form.validate_on_submit():

        upload_session = upload_songs(form.files.data)
        return upload_session
        # return redirect(url_for('songs.songs'))
    
    return render_template('upload.html', form=form)


############################################################
# Route for uploading songs
# Can get files from anyway and fill return upload session
# if any files got uploaded succesfull.
# TODO BASICS, rewrite, split responsibilities
############################################################
def upload_songs(files) -> None:

    # Songs that got succesfully uploaded
    uploaded_files = []

    # Songs that get uploaded belong to an upload session, so later we can edit these songs together.
    upload_session_uuid = uuid.uuid4().int>>32
    upload_session_uuid = str(upload_session_uuid).zfill(32)

    for f in files:
        # To make sure all our filenames are unique, we prefix all files with a short UUID
        song_uuid = uuid.uuid4().int>>32
        song_uuid = str(song_uuid)
        song_uuid = song_uuid[:8].zfill(8)

        secure_file_name = secure_filename(f.filename)

        # Should only be .mp3 right now
        try:
            extension = secure_file_name.split('.').pop().lower()
            if extension.lower() != 'mp3':
                flash("Cannot upload files that are not ''mp3'")
                continue
        except Exception as e:
            continue
        
        filename_with_uuid = f"[{song_uuid}]_{secure_file_name}"
        path_and_file = os.path.join(app.config['TEMP_FOLDER'], filename_with_uuid)
        f.save(path_and_file)
        uploaded_files.append(filename_with_uuid)

        meta_title = 'unknown song'
        meta_artist = None
        meta_album = None
        file_cover = None
        meta_duration_in_sec = -1


        try: 
            meta_file = eyed3.load(path_and_file)
            if meta_file.tag is None:
                raise Exception("No tag was found to retrieve metadata")
            if meta_file.tag:
                p_err('BEEP BOOP')
                meta_title = meta_file.tag.title
                p_err('Tried to get artist meta')
                meta_artist = meta_file.tag.artist
                meta_album = meta_file.tag.album

            if meta_file.info is None:
                raise(Exception('No info was found for this file. Is it broken?'))
            meta_duration_in_sec = meta_file.info.time_secs
    
        except Exception as e:
            print(f"Failed opening file with eye3d: {e}")

                        
        meta_image = None
        for image in meta_file.tag.images:
            # Check if image already exists, else we store it
            image_md5 = hashlib.md5(image.image_data).hexdigest()
            path_for_image = os.path.join(os.path.join(app.config['DATA_FOLDER'], 'songs_covers', f'{image_md5}.png'))
            path_for_icon = os.path.join(os.path.join(app.config['DATA_FOLDER'], 'songs_covers_icon', f'{image_md5}.png'))
            if os.path.isfile(path_for_image):
                print('File already exits! No reason to store again!')
            else:
                image_file = open(path_for_image, 'wb')
                image_file.write(image.image_data)
                image_file.close()

                # Make thumbnail
                image_to_resize = Image.open(path_for_image)
                icon = image_to_resize.resize((128, 128))
                icon.save(path_for_icon)
            # Just support one cover for now
            file_cover = f"{image_md5}.png"
            break

        

        # Check if artist exist, if so. Get the id
        # If not exist, create the artist!
        if meta_artist is None:
            temp = None
            pass
        else:
            artist = None
            artist = Artist.query.filter(func.lower(Artist.name) == func.lower(meta_artist)).first()
            print(f'QUERY RESULT: {artist}')

            if artist:
                temp = artist.id
                p_note(f'EXISTING ARTIST with ID : {temp}')
            else:
                temp = create_artist(meta_artist)
                p_note(f'NEW ARTIST with ID : {temp}')
            # We are gonna create the artist!



        # Add query to DB
        song = Song(title=meta_title,
                    # artist=None, # THIS LITTLE FUCKER WAS CAUSING THE OTHER ARTIST_ID TO OVERRIDE
                    album=None,
                    length_in_sec=meta_duration_in_sec,
                    extension=extension,
                    file_name=filename_with_uuid,
                    user_id=current_user.id,
                    artist_id=temp,
                    album_id=0,
                    file_cover=file_cover,
                    upload_session=upload_session_uuid
                    )
        
        
        p_note(f'THIS AFTER{song.artist_id}')
            
        db.session.add(song)

        # Commit db info once all files are uploaded and images are generated succesfully. 
        db.session.commit()

        p_err(song.artist_id)
        p_err(song.user_id)

        # Now move files to persistent folder and mark files as moved succesfull
        
            
    for file in uploaded_files:
        try:
            temp = os.path.join(os.path.join(app.config['DATA_FOLDER'], 'temp', file))
            files = os.path.join(os.path.join(app.config['DATA_FOLDER'], 'songs', file))
            os.rename(temp, files)

            # Mark file stored safely
            db.session.query(Song). \
            filter(Song.file_name == file). \
            update({'moved_to_songs': True})
            db.session.commit()
        except Exception as e:
            # If file moving didn't work, mark files 'dead'
            db.session.query(Song). \
            filter(Song.file_name == file). \
            update({'alive': False})
            db.session.commit()
            flash(f"Failed to upload file {file} Trace: {e}")

    return upload_session_uuid


############################################################
# Route for seeing songs
# Can get files from anyway and fill return upload session
# if any files got uploaded succesfull.
# TODO BASICS, rewrite, split responsibilities
############################################################
@bp_songs.route('/songs', methods=['GET', 'POST'])
def songs():
    title = 'MusicDB :: Song list'

    if not current_user.is_authenticated:
        flash('Please login to start uploading.')
        return redirect(url_for('users.login'))
    
    song_for_display = []
    class s():
        # General
        title = None
        album = None
        artist = None
        length = None
        is_favorite = False
        is_owner = True

        # CDN
        cdn_song_icon = None
        cdn_song_file = None
        # cdn_song_download = None # I think I can use the cdn_song_file for that, for now.

        # URLs
        url_to_song = None
        url_to_album = None
        url_to_artist = None
    
    songs_from_db = Song.query.all()

    for song in songs_from_db:
        temp = s()

        #GENERAL

        temp.title = song.title
        # TODO implement album
        temp.album = None
        temp.artist = db.session.query(Artist.name).filter(Artist.id == song.artist_id).first()
        if temp.artist:
            temp.artist = temp.artist[0]


        temp.length = sec_to_str(song.length_in_sec)

        # TODO implement favs
        temp.is_favorite = None

        # CDN
        if song.file_cover:
            temp.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
            temp.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)

        # TODO implement song page
        temp.url_to_song = None
        # TODO implement album page
        temp.url_to_album = None
        temp.url_to_artist = parse_artist_url(song.artist)

        song_for_display.append(temp)

    return render_template('songs.html', title=title, songs=song_for_display)


############################################################
# Time in sec represented in a string format
############################################################
def sec_to_str(time: int) -> str:
    if time == -1:
        return 'E:RR'
    
    sec = time % 60
    sec = math.floor(sec)
    sec = str(sec).zfill(2)
    min = math.floor(time / 60)



    time = 5
    return f"{min}:{sec}"

