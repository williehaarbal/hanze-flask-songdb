from werkzeug.utils import secure_filename
from musicdb.models import Song
from flask_login import current_user
from musicdb import app, db
from flask import Blueprint, flash, redirect, render_template, url_for
from .forms import UploadForm
from PIL import Image
import hashlib
import eyed3
import uuid
import os

bp_songs = Blueprint('songs', __name__)

# TODO: add orig filename
@bp_songs.route('/upload', methods=['GET', 'POST'])
def upload():

    if not current_user.is_authenticated:
        flash('Please login to start uploading.')
        return redirect(url_for('bp_songs.login'))
    
    form = UploadForm()
    if form.validate_on_submit():

        uploaded_files = []
        upload_session_uuid = uuid.uuid4().int>>32
        upload_session_uuid = str(upload_session_uuid).zfill(32)

        for file in form.files.data:

            # To make sure all our filenames are unique, we prefix all files with a short UUID
            song_uuid = uuid.uuid4().int>>32
            song_uuid = str(song_uuid)
            song_uuid = song_uuid[:8].zfill(8)

            
            print(f'Before: {song_uuid}')

            secure_file_name = secure_filename(file.filename)

            # Should only be .mp3 right now
            extension = secure_file_name.split('.').pop().lower()
            if extension != 'mp3':
                flash("Cannot upload files that are not ''mp3'")
                break

            filename_with_uuid = f"[{song_uuid}]_{secure_file_name}"
            path_and_file = os.path.join(app.config['TEMP_FOLDER'], filename_with_uuid)
            file.save(path_and_file)
            uploaded_files.append(filename_with_uuid)

            # Get meta data of song

            meta_title = 'unknown title'
            meta_artist = 'unknown artist'
            meta_album = 'unknown album'
            meta_duration_in_sec = -1

            try: 
                meta_file = eyed3.load(path_and_file)
                if meta_file.tag is None:
                    raise Exception("No tag was found to retrieve metadata")
                if meta_file.tag:
                    meta_title = meta_file.tag.title
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
                break

            # Add query to DB
            song = Song(title=meta_title,
                        artist=None,
                        album=None,
                        length_in_sec=meta_duration_in_sec,
                        extension=extension,
                        file_name=filename_with_uuid,
                        file_cover=f"{image_md5}.png",
                        upload_session=upload_session_uuid
                        )
            
            db.session.add(song)

        # Commit db info once all files are uploaded and images are generated succesfully. 
        db.session.commit()

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

        return redirect(url_for('songs.songs'))
    
    return render_template('upload.html', form=form)


@bp_songs.route('/songs', methods=['GET', 'POST'])
def songs():
    if not current_user.is_authenticated:
        flash('Please login to start uploading.')
        return redirect(url_for('users.login'))

    songlist = Song.query.all()

    return render_template('songs.html', songlist=songlist)
