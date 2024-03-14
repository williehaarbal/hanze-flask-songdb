from musicdb.bp_albums.func import generate_album_list
from musicdb.bp_albums.templates.forms import UpdateAlbum
from musicdb.bp_main.routes import sec_to_str
from musicdb.bp_songs.func import generate_song_list
from musicdb.models import Album, Artist, Song
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from musicdb import db, DEBUG
from musicdb.general import country_icon_list, p_err, p_note
# from .forms import CreateArtist
from typing import TypedDict
from flask import Blueprint, flash, redirect, render_template, request, url_for
import hashlib
import shutil
import os

# Flask blueprint definition
bp_albums = Blueprint('albums', __name__, template_folder='templates')

############################################################
# SHOW ALBUMS
############################################################
@bp_albums.route('/albums')
def albums():
    
    # GENERAL :: page title
    title = 'MusicDB :: Albums'
    # GENERAL :: Current page
    current_page = request.url

    if not current_user.is_authenticated:
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))
    
    # Paginate settings
    # TODO implement some form of paginate for albums
    page = request.args.get('page', 1, type=int)
    entries_per_page = 8

    
    # Get all album objects from database
    albums_retrieved_from_database = db.session.scalars(db.select(Album)).all()
    
    albums_for_display, albums_retrieved_from_database = generate_album_list(page=page, entries_per_page=entries_per_page, albums_retrieved_from_database=albums_retrieved_from_database, current_page=current_page)
    
    return render_template('albums.html', title=title, albums=albums_for_display)


############################################################
# CREATE ALBUM
############################################################
@bp_albums.route('/album/add')
def route_album_add():
    pass

############################################################
# FUNC ::  CREATE ALBUM
############################################################
def create_album(name: str, **kwargs):
    """
    Responsibility:
    - Parsing, saving and storing album cover
    - adding entry to database
    """


    album_name = name
    album_description = None
    album_cover = None
    album_artist = None
    album_cover_copy = None

    for arg in kwargs:
        if str(arg) == 'album_description':
            album_description = kwargs[arg]
        if str(arg) == 'album_cover':
            album_cover = kwargs[arg]
        if str(arg) == 'album_artist':
            album_artist = kwargs[arg]
        if str(arg) == 'album_cover_copy':
            album_cover_copy = kwargs[arg]
        
    # In case of outside runtime call
    from musicdb.models import Album
    from musicdb import db, app

    if album_cover:
        filename = album_cover.filename
        temp = os.path.join(app.config['TEMP_FOLDER'], filename)
        album_cover.save(temp)
        file_ext = filename.split('.').pop().lower()

        # Avoid double album covers

        md5_of_file = hashlib.md5(open(temp, 'rb').read()).hexdigest()
        hashed_name = (f"{md5_of_file}.{file_ext}")
        persistent = os.path.join(os.path.join(app.config['ALBUM_COVER'], hashed_name))

        album_cover = hashed_name

        try:
            if not os.path.isfile(persistent):
                os.rename(temp, persistent)
        except Exception as e:
            try:
                os.remove(temp)
                album_cover = None
            except:
                album_cover = None
                pass

    if album_cover_copy:
        try:
            # Copy the file from songs_covers -> album_covers
            
            from_file = os.path.join(os.path.join(app.config['SONG_COVER'], album_cover_copy))
            to_file = os.path.join(os.path.join(app.config['ALBUM_COVER'], album_cover_copy))
            if os.path.isfile(to_file):
                pass
            else:
                shutil.copy(from_file, to_file)
            album_cover=album_cover_copy
            
        except:
            album_cover = None
            
    
    try:
        new_album = Album(
            name = album_name,
            description = album_description,
            album_cover = album_cover,
            artist=album_artist
        )
        db.session.add(new_album)
        db.session.commit()
        p_note(new_album)
        return new_album.id
    except Exception as e:
        p_err(f'ERROR WHILE CREATING ALBUM :: {e}')
        pass



############################################################
# SHOW SINGLE ALBUM
# Naam
# Omschrijving
# Cover
# Artist
# lijst alle nummers in album
############################################################
@bp_albums.route('/album/<id>')
def album(id):
    
    album_id = id
    
    # General page info
    title = 'MusicDB'
    
    if not current_user.is_authenticated:
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))
    
    entries_per_page = 1000
    page = 1
    # GENERAL :: Current page
    current_page = request.url
    
    album_info = db.session.query(Album).filter(Album.id == album_id).first()
    
    class album():
        name = album_info.name
        artist = album_info.artist.name
        description = album_info.description
        url_to_edit = f'{request.url}/edit'
        album_cover = url_for('utils.cdn_album_cover', filename=album_info.album_cover)
    
    songs_retrieved_from_database = Song.query.filter(Song.alive==True, Song.album_id == id).paginate(page=page, per_page=entries_per_page)
    
    
    songs_for_display , songs_retrieved_from_database = generate_song_list(page=page, entries_per_page=entries_per_page, songs_retrieved_from_database=songs_retrieved_from_database, current_page=current_page)

    
    
    return render_template("album.html", album=album, songs=songs_for_display)


############################################################
# ROUTE :: Edit album
############################################################
@bp_albums.route('/album/<album_id>/edit', methods=['GET', 'POST'])
def album_edit(album_id):

    if not current_user.is_authenticated:
        flash('Please login to start using this size.')
        return redirect(url_for('users.login'))

    # GENERAL FOR PAGE

    # GET SONG OBJECT
    album_from_db = Album.query.filter_by(id=album_id).first()
    
    if album_from_db is None:
        return redirect(url_for('main.not_found'))

    title = f'MusicDB :: {album_from_db.name}'

    # FORM DEFINITIONS
    form = UpdateAlbum()

    
    # List all artists
    artist_choices = ['<unknown>']
    all_artists_from_db = db.session.scalars(db.select(Artist.name)).all()
    for a in all_artists_from_db:
        artist_choices.append(a)
    form.artist.choices = artist_choices

    # POSTING
    if form.validate_on_submit():
        p_note('VALIDATED')
        album_from_db.name = form.name.data
        next_artist = form.artist.data
        next_artist = Artist.query.filter_by(name=next_artist).first()
        album_from_db.artist = next_artist
        album_from_db.description = form.description.data

        db.session.commit()
        flash(f'Song updated!')
        

    # FORM :: name
    form.name.data = album_from_db.name

    # FORM :: artist
    artist_choices = ['<unknown>']
    all_artists_from_db = db.session.scalars(db.select(Artist.name)).all()
    for a in all_artists_from_db:
        artist_choices.append(a)
    form.artist.choices = artist_choices
    if album_from_db.artist is not None:
        form.artist.data = album_from_db.artist.name
    else:
        form.artist.data = '<unknown>'

    
    form.description.data = album_from_db.description

    # Get URL for filecover
    if album_from_db.album_cover:
        cover = url_for('utils.cdn_album_cover', filename=album_from_db.album_cover)
    else:
        cover = None
    



    
    return render_template('album_edit.html', title=title, form=form, cover=cover, album=album_from_db)