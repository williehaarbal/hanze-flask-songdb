import math
from musicdb.bp_albums.func import generate_album_list
from musicdb.bp_artists.func import generate_artist_list, generate_artist_page
from musicdb.bp_songs.func import generate_song_list
from musicdb.bp_utils.func import sec_to_str
from musicdb.models import Album, Artist, Song
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from musicdb import db, DEBUG
from musicdb.general import country_icon_list, p_err, p_note
from .forms import CreateArtist

from typing import TypedDict
from flask import Blueprint, flash, redirect, render_template, request, url_for
import hashlib
import os

# Flask blueprint definition
bp_artists = Blueprint('artists', __name__, template_folder='templates')

############################################################
# Route for displaying all artist.
# TODO BASICS
############################################################
@bp_artists.route("/artists")
def artist_list():

    if not current_user.is_authenticated:
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))

    # General
    title = 'MusicDB :: artists'
    page = request.args.get('page', 1, type=int)
    entries_per_page = 4
    current_page = 0

    # Query a part of the artist to display on page
    artists_retrieved_from_database = Artist.query.paginate(page=page, per_page=entries_per_page)

    artist_for_display, artists_retrieved_from_database = generate_artist_list(page=page, entries_per_page=entries_per_page, artists_retrieved_from_database=artists_retrieved_from_database, current_page=current_page)
    
    return render_template('list_artist.html', title=title, artists=artist_for_display, paginate=artists_retrieved_from_database)


############################################################
# Route for displaying a single artist
# TODO BASICS, REWRITE
############################################################
@bp_artists.route("/artist/<id>")
def artist(id):

    if not current_user.is_authenticated:
        flash('Please login to start uploading.')
        return redirect(url_for('users.login'))
    
    # GENERAL :: Title for page
    title = f'MusicDB :: {db.session.query(Artist).filter(Artist.id == id).first().name}'
    # GENERAL :: Current page
    current_page = request.url
    # Paginate for lists
    album_page = request.args.get('album_page', 1, type=int)
    song_page = request.args.get('song_page', 1, type=int)
    album_entries_per_page = 2
    song_entries_per_page = 5


    ##### ARTIST ######
    # Retrieve the artist for this page
    artist_retrieved_from_database = db.session.query(Artist).filter(Artist.id == id).first()
    artist = generate_artist_page(artist_retrieved_from_database)

    ##### ABLUMS #####
    # Get all album objects from database
    albums_retrieved_from_database = Album.query.filter(Album.artist_id == id).paginate(page=album_page, per_page=album_entries_per_page)
    
    # Convert database entries in a nice paginate object list
    albums, album_paginate = generate_album_list(page=album_page, entries_per_page=album_entries_per_page, albums_retrieved_from_database=albums_retrieved_from_database, current_page=current_page)
    
    ##### SONGS #####
    # Get all songs from the database
    songs_retrieved_from_dataabse = Song.query.filter(Song.artist_id == id).paginate(page=song_page, per_page=song_entries_per_page)
    songs, song_paginate = generate_song_list(page=song_page, entries_per_page=song_entries_per_page, songs_retrieved_from_database=songs_retrieved_from_dataabse, current_page=current_page)
    
    return render_template('artist.html', title=title, artist=artist, albums=albums, album_paginate=album_paginate, songs=songs, song_paginate=song_paginate)


############################################################
# Route for creating artist page
# TODO BASICS, rewrite?
############################################################
@bp_artists.route("/artists/add", methods=['GET', 'POST'])
def artist_add():

    if not current_user.is_authenticated:
        flash("You shouldn't be here.")
        redirect(url_for('main.home'))

    errors = None
    title = "MusicDB :: new artist"

    form = CreateArtist()

    if form.validate_on_submit():
        try:
            create_artist(form.name.data, band_cover=form.picture.data, description=form.description.data, country=form.country_flag.data)
            flash('New artist created!')
        except Exception as e:
            flash(f'Error creating new artist. ERROR: {e}')

    return render_template('create_artist.html', form=form, title=title)


############################################################
# Function to create artist objects in database
# TODO BASICS, clean, notifications, error handling?
############################################################
def create_artist(name:str, **kwargs) -> int:

    # Name is mandetory, other args are optional.
    description = None
    country = None
    band_cover = None

    # Check if aditional arguments are given.
    for arg in kwargs:
        if str(arg) == 'description':
            description = kwargs[arg]
        if str(arg) == 'country':
            country = kwargs[arg]
        if str(arg) == 'band_cover':
            band_cover = kwargs[arg]
    
    # In case of outside runtime call
    from musicdb.models import Artist
    from musicdb import db, app

    excist = db.session.query(Artist.id).filter_by(name = name).first() is not None

    if excist:
        raise Exception('Artist already exists!')
    else:
        # ARTIST DOESN'T EXCIST
        md5_and_extention = None
        if band_cover:
            filename = band_cover.filename
            temp = os.path.join(app.config['TEMP_FOLDER'], filename)
            band_cover.save(temp)
            extension = filename.split('.').pop().lower()
            
            md5 = hashlib.md5(open(temp, 'rb').read()).hexdigest()
            md5_and_extention = f'{md5}.{extension}'
            persistent = os.path.join(os.path.join(app.config['BAND_COVER'], md5_and_extention))

            if band_cover:
                try:
                    if not os.path.isfile(persistent):
                        os.rename(temp, persistent)
                except Exception as e:
                    os.remove(temp)
                    print(e)
    
        new_artist = Artist(name=name, country=country, band_cover=md5_and_extention, description=description)
        db.session.add(new_artist)
        db.session.commit()
        return new_artist


############################################################
# FUNC :: parse artist name
# TODO better save handling
############################################################
def parse_artist_url(artist: str) -> str:
    """
        'Some Band' -> 'some-band'
    """
    if artist is None:
        return None
    safe_artist_name = artist.name.replace(" ", "-").lower()
    return url_for('artists.artist', arg_artist=safe_artist_name)

############################################################
# FUNC :: parse artist name
# TODO better save handling
############################################################
def parse_artist_url(artist: str) -> str:
    """
        'some-band' -> 'some band'
    """
    if artist is None:
        return None
    
    safe_artist_name = artist.name.replace(" ", "-").lower()
    return url_for('artists.artist', id=safe_artist_name)

