import math
from sqlalchemy import func, text
from werkzeug.utils import secure_filename
from musicdb.bp_albums.routes import create_album
from musicdb.bp_artists.routes import create_artist, parse_artist_url
from musicdb.bp_utils.func import sec_to_str
from musicdb.models import Album, Artist, Song, UsersLikesSongs
from flask_login import current_user
from musicdb import app, db
from musicdb.general import p_err, p_note
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from .forms import UpdateSong, UploadForm
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
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))
    
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
    created_albums = {} # name : album.id

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

        artist_object = None

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
                artist_object = artist
            else:
                artist_object = create_artist(meta_artist)
            # We are gonna create the artist!
        
        # Make albums
        
        if meta_album is None:
            meta_album_id = None
        else:
            if meta_album in created_albums:
                meta_album_id = created_albums[meta_album]
            else:
                # Create a new album
                meta_album_id = create_album(name=meta_album, album_artist=artist_object, album_cover_copy=file_cover)
                created_albums[meta_album] = meta_album_id


        p_note(f'Meta album id: {meta_album_id}')
        # Add query to DB
        song = Song(title=meta_title,
                    # artist=None, # THIS LITTLE FUCKER WAS CAUSING THE OTHER ARTIST_ID TO OVERRIDE
                    # album=None, # ALMOST FELL FOR THIS SHIT TWICE
                    length_in_sec=meta_duration_in_sec,
                    extension=extension,
                    file_name=filename_with_uuid,
                    user_id=current_user.id,
                    artist=artist_object,
                    album_id=meta_album_id,
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
    
    # GENERAL :: page title
    title = 'MusicDB :: Song list'
    
    # Pagination settings
    page = request.args.get('page', 1, type=int)
    entries_per_page = 10

    # Cannot show page if visitor is logged in.
    if not current_user.is_authenticated:
        flash('Please login to start using this functionality.')
        return redirect(url_for('users.login'))
    
    
    class Song_info_container():
        # General
        id = None
        title = None
        album = None
        artist = None
        length = None
        favorite = None
        is_owner = False # TODO Not implemented yet

        # CDN
        # (These are 'links' the browser can interpret to get files likes images, the mp3s and suchs)
        cdn_song_icon = None
        cdn_song_file = None

        # URLs
        # Links to other pages that relate to this song
        url_to_song = None
        url_to_album = None
        url_to_artist = None
        url_to_like = None
        url_to_unlike = None
        
    # Holds all the song objects in an list that will be able to be looped over with Flask render_template.
    song_for_display = []
    
    # Get a list up to 10 songs (by paginate & that are 'alive' / not deleted).
    songs_retrieved_from_database = Song.query.filter(Song.alive==True).paginate(page=page, per_page=entries_per_page)

    for song in songs_retrieved_from_database:
        
        # Because this is a collection of multiple songs we create objects instead of using the class to hold our information.
        song_object = Song_info_container()

        # Get song id
        song_object.id = song.id
        # Get title
        song_object.title = song.title
        # Get artist
        if song.artist:
            song_object.artist = song.artist.name
        else:
            song_object.artist = "Unknown artist"
        # Get album
        if song.album:
            song_object.album = song.album.name
        else:
            song_object.album = "Unknown album"
        # Get the length of the song
        song_object.length = sec_to_str(song.length_in_sec)
        # Is favorite
        if UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song.id).first() is None:
            song_object.favorite = False
        else:
            song_object.favorite = True
    
        # CDN
        # Get song cover
        if song.file_cover:
            song_object.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
        # Get music file
            song_object.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)

        # URL to song
        song_object.url_to_song = f'/song/{song.id}'
        # URL to artist
        song_object.url_to_artist = f'/artist/{song.artist_id}'
        # URL to album
        song_object.url_to_album = f'/album/{song.album_id}'
        
        # Get the URL of the current page. If a user 'likes' or 'unlikes' a song, it calls a route that handles liking/unliking. Then redirects to the page it was already on. (refreshes for updates page.) Very hacky. Works somehow like a charm.
        # Done this way so you can like/unlike from multiple different pages.
        current_page = request.url
        
        # URL to like
        # Passes the current page as a argument
        song_object.url_to_like = f'/song/{song_object.id}/like?current_page={current_page}'
        # URL to unlike
        # Passes the current page as a argument
        song_object.url_to_unlike = f'/song/{song_object.id}/unlike?current_page={current_page}'

        song_for_display.append(song_object)
        
        
    for i in song_for_display:
        p_note(i.favorite)

    return render_template('songs.html', title=title, songs=song_for_display, paginate=songs_retrieved_from_database)

############################################################
# REDIRECT :: Like song by user
############################################################
@bp_songs.route("/song/<song_id>/like", methods=['GET','POST'])
def action_like_song(song_id):
    current_page = request.args.get('current_page', None)
    like = UsersLikesSongs()
    like.user_id = int(current_user.id)
    like.song_id = int(song_id)
    db.session.add(like)
    db.session.commit()
    return redirect(current_page)

############################################################
# REDIRECT :: Unlike song by user
############################################################
@bp_songs.route("/song/<song_id>/unlike", methods=['GET','POST'])
def action_unlike_song(song_id):
    current_page = request.args.get('current_page', None)
    response = UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song_id).all()
    for r in response:
        db.session.delete(r)
    db.session.commit()
    return redirect(current_page)

############################################################
# ROUTE :: Song
############################################################
@bp_songs.route('/song/<song_id>', methods=['GET', 'POST'])
def song(song_id):

    # If the current user isn't authenticated (anonymouse), then redirect him/her to login page.
    if not current_user.is_authenticated:
        flash('Please login to access songs...')
        return redirect(url_for('users.login'))

    # Get some object from database
    song_retrieved_from_database = Song.query.filter_by(id=song_id).first()
    # If song not found, throw an error
    # TODO Is this proper error handing here?
    if song_retrieved_from_database is None:
        abort(500)

    # GENERAL :: title
    title = f'MusicDB :: {song_retrieved_from_database.title}'

    # A class that acts as a container to hold info over a song (single object = single song)
    class song_container():
        # General
        title = None
        artist = None
        album = None
        length = None
        favorite = None
        
        # CDN
        cdn_song_file = None
        cdn_song_cover = None
        cdn_artist_country_flag = None
        
        # URLs
        url_to_artist = None
        url_to_album = None
        url_to_edit = None
        url_to_like = None
        url_to_unlike = None
        
    # Get title
    song_container.title = song_retrieved_from_database.title
    # Get artist
    if song_retrieved_from_database.artist:
        song_container.artist = song_retrieved_from_database.artist.name
    # Get album
    if song_retrieved_from_database.album:
        song_container.album = song_retrieved_from_database.album.name
    # Get length
    if song_retrieved_from_database.length_in_sec:
        song_container.length = sec_to_str(song_retrieved_from_database.length_in_sec)
        
        
    # Is favorite
    if UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song_retrieved_from_database.id).first() is None:
        song_container.favorite = False
    else:
        song_container.favorite = True
    
    # CDN
    # Get song cover
    if song_retrieved_from_database.file_cover:
        song_container.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song_retrieved_from_database.file_cover)
    # Get music file
    if song_retrieved_from_database.file_name:
        song_container.cdn_song_file = url_for('utils.cdn_songs', filename=song_retrieved_from_database.file_name)
    # Get country flag
    if song_retrieved_from_database.artist.country:
        p_note('trigger')
        song_container.cdn_artist_country_flag = url_for('utils.cdn_flags', long_country_name=song_retrieved_from_database.artist.country)
    else:
        song_container.cdn_artist_country_flag = url_for('utils.cdn_flags', long_country_name='world')
    # URL to edit
    song_container.url_to_edit = f'/song/{song_retrieved_from_database.id}/edit'
    # URL to artist
    song_container.url_to_artist = f'/artist/{song_retrieved_from_database.artist_id}'
    # URL to album
    song_container.url_to_album = f'/album/{song_retrieved_from_database.album_id}'
    
    # Get the URL of the current page. If a user 'likes' or 'unlikes' a song, it calls a route that handles liking/unliking. Then redirects to the page it was already on. (refreshes for updates page.) Very hacky. Works somehow like a charm.
    # Done this way so you can like/unlike from multiple different pages.
    current_page = request.url
    
    # URL to like
    # Passes the current page as a argument
    song_container.url_to_like = f'/song/{song_retrieved_from_database.id}/like?current_page={current_page}'
    # URL to unlike
    # Passes the current page as a argument
    song_container.url_to_unlike = f'/song/{song_retrieved_from_database.id}/unlike?current_page={current_page}'

    return render_template('song.html', title=title, song=song_container)

############################################################
# Route for uploading songs
# Can get files from anyway and fill return upload session
# if any files got uploaded succesfull.
# TODO BASICS, rewrite, split responsibilities
############################################################
@bp_songs.route('/song/<song_id>/edit', methods=['GET', 'POST'])
def song_edit(song_id):

    if not current_user.is_authenticated:
        flash('Please login to start using this size.')
        return redirect(url_for('users.login'))

    # GENERAL FOR PAGE

    # GET SONG OBJECT
    song_from_db = Song.query.filter_by(id=song_id).first()
    
    if song_from_db is None:
        return redirect(url_for('main.not_found'))


    
    title = f'MusicDB :: {song_from_db.title}'

    # FORM DEFINITIONS
    form = UpdateSong()

    
    form.alive.choices = ["True", "False"]

    artist_choices = ['<unknown>']
    all_artists_from_db = db.session.scalars(db.select(Artist.name)).all()
    for a in all_artists_from_db:
        artist_choices.append(a)
    form.artist.choices = artist_choices

    album_choices = ['<unknown>']
    all_albums_from_db = Album.query.filter(Album.artist_id == song_from_db.artist_id).all()
    for album in all_albums_from_db:
        if album.name:
            album_choices.append(album.name)
        else:
            # Niks?
            pass
    form.album.choices = album_choices


    # POSTING
    if form.validate_on_submit():
        p_note('VALIDATED')
        next_name = form.title.data
        next_album = form.album.data
        next_artist = form.artist.data
        alive = form.alive.data

        p_note(f'{next_name}, {next_album}, {next_artist}, {alive}')

        artist_object = Artist.query.filter_by(name=next_artist).first()
        album_object = Album.query.filter_by(name=next_album).first()
        p_note(f'{artist_object}, {album_object}')
        p_err(next_name)
        song_from_db.title = next_name
        if alive == 'True':
            song_from_db.alive = True
        else:
            song_from_db.alive = False
        
        song_from_db.album = album_object

        song_from_db.artist = artist_object

        db.session.commit()

    # FORM :: name
    form.title.data = song_from_db.title

    # FORM :: artist
    artist_choices = ['<unknown>']
    all_artists_from_db = db.session.scalars(db.select(Artist.name)).all()
    for a in all_artists_from_db:
        artist_choices.append(a)
    form.artist.choices = artist_choices
    if song_from_db.artist is not None:
        form.artist.data = song_from_db.artist.name
    else:
        form.artist.data = '<unknown>'

    # FORM :: album
    album_choices = ['<unknown>']
    all_albums_from_db = Album.query.filter(Album.artist_id == song_from_db.artist_id).all()
    for album in all_albums_from_db:
        if album.name:
            album_choices.append(album.name)
        else:
            # Niks?
            pass
    form.album.choices = album_choices
    if song_from_db.album is not None:
        form.album.data = song_from_db.album.name
    else:
        form.album.data = '<unknown>'

    # FORM :: alive
    form.alive.choices = ["True", "False"]
    if song_from_db.alive:
        form.alive.data = "True"
    else:
        form.alive.data = "False"

    # Get URL for filecover
    if song_from_db.file_cover:
        cover = url_for('utils.cdn_song_big', filename=song_from_db.file_cover)
    else:
        cover = None
    



    
    return render_template('song_edit.html', title=title, form=form, cover=cover, song=song_from_db)
    

@bp_songs.route('/song/remove/<id>', methods=['POST', 'GET'])
def remove_song(id):
    query = text(f'DELETE FROM song where id={id};')
    db.session.execute(query)
    db.session.commit()
    return '204'


############################################################
# ROUTE :: Likes
############################################################
@bp_songs.route('/likes', methods=['GET', 'POST'])
def likes():
    
    # GENERAL :: page title
    title = 'MusicDB :: liked songs'
    
    # Pagination settings
    page = request.args.get('page', 1, type=int)
    entries_per_page = 10

    # Cannot show page if visitor is logged in.
    if not current_user.is_authenticated:
        flash('Please login to start using this functionality.')
        return redirect(url_for('users.login'))
    
    
    class Song_info_container():
        # General
        id = None
        title = None
        album = None
        artist = None
        length = None
        favorite = None
        is_owner = False # TODO Not implemented yet

        # CDN
        # (These are 'links' the browser can interpret to get files likes images, the mp3s and suchs)
        cdn_song_icon = None
        cdn_song_file = None

        # URLs
        # Links to other pages that relate to this song
        url_to_song = None
        url_to_album = None
        url_to_artist = None
        url_to_like = None
        url_to_unlike = None
        
    # Holds all the song objects in an list that will be able to be looped over with Flask render_template.
    song_for_display = []
    
    # Get a list up to 10 songs (by paginate & that are 'alive' / not deleted).
    songs_retrieved_from_database = Song.query.filter(
        Song.alive==True,
        UsersLikesSongs.user_id==current_user.id,
        UsersLikesSongs.song_id==Song.id
        ).paginate(page=page, per_page=entries_per_page)

    for song in songs_retrieved_from_database:
        
        # Because this is a collection of multiple songs we create objects instead of using the class to hold our information.
        song_object = Song_info_container()

        # Get song id
        song_object.id = song.id
        # Get title
        song_object.title = song.title
        # Get artist
        if song.artist:
            song_object.artist = song.artist.name
        else:
            song_object.artist = "Unknown artist"
        # Get album
        if song.album:
            song_object.album = song.album.name
        else:
            song_object.album = "Unknown album"
        # Get the length of the song
        song_object.length = sec_to_str(song.length_in_sec)
        # Is favorite
        if UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song.id).first() is None:
            song_object.favorite = False
        else:
            song_object.favorite = True
    
        # CDN
        # Get song cover
        if song.file_cover:
            song_object.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
        # Get music file
            song_object.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)

        # URL to song
        song_object.url_to_song = f'/song/{song.id}'
        # URL to artist
        song_object.url_to_artist = f'/artist/{song.artist_id}'
        # URL to album
        song_object.url_to_album = f'/album/{song.album_id}'
        
        # Get the URL of the current page. If a user 'likes' or 'unlikes' a song, it calls a route that handles liking/unliking. Then redirects to the page it was already on. (refreshes for updates page.) Very hacky. Works somehow like a charm.
        # Done this way so you can like/unlike from multiple different pages.
        current_page = request.url
        
        # URL to like
        # Passes the current page as a argument
        song_object.url_to_like = f'/song/{song_object.id}/like?current_page={current_page}'
        # URL to unlike
        # Passes the current page as a argument
        song_object.url_to_unlike = f'/song/{song_object.id}/unlike?current_page={current_page}'

        song_for_display.append(song_object)
        
        
    for i in song_for_display:
        p_note(i.favorite)

    return render_template('likes.html', title=title, songs=song_for_display, paginate=songs_retrieved_from_database)
