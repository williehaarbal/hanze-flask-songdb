from musicdb.models import Artist
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
bp_artists = Blueprint('artists', __name__)

############################################################
# Route for displaying all artist.
# TODO BASICS
############################################################
@bp_artists.route("/artists")
def artist_list():

    if not current_user.is_authenticated:
        redirect(url_for('main.home'))

    # General
    title = 'MusicDB :: artists'
    page = request.args.get('page', 1, type=int)
    entries_per_page = 4

    # This object holds our info from database, as well extra data like URL's and suchs.
    # These objects will be stored in 'artist_for_this_page' and then passed to the renderer.
    artists_for_this_page = []
    class Temp_artist():
        name = None
        country_icon = None
        description = None
        cover_img = None
        amount_songs = None
        amount_albums = None

        # URLS

        url_to_artist = None
        url_to_albums = None
        url_to_songs = None

        def __repr__(self) -> str:
            return f"TEMP ARTIST OBJECT :: {self.name}, {self.country_icon}, {self.description}, {self.cover_img}, {self.amount_songs}, {self.amount_albums}, {self.url_to_artist}, {self.url_to_albums}, {self.url_to_songs}"

    # Query a part of the artist to display on page
    artists_from_db = Artist.query.paginate(page=page, per_page=entries_per_page)

    for artist in artists_from_db:
        temp = Temp_artist()

        # Name
        temp.name = artist.name

        # Country icon
        # These are the current supported countries with their abbr.
        from musicdb.general import country_icon_list

        if artist.country:
            try:
                abbr = country_icon_list[artist.country]
                abbr = f'{abbr}.svg'
                # Flags are stored in 'static/flags' folder
                path = f'flags/{abbr}'
                temp.country_icon = url_for('static', filename=path)
            except KeyError as KE:
                path = f'flags/xx.svg'
                temp.country_icon = url_for('static', filename=path)
                if DEBUG:
                    print(f"artist_list :: convert to svg name :: ERROR: {KE} ")
        else:
            path = f'flags/xx.svg'
            temp.country_icon = url_for('static', filename=path)
            temp.country_icon = ''

        # Description
        # Makes the description able to hold markup
        temp.description = Markup(artist.description)

        # Cover image
        if artist.band_cover:
            temp.cover_img = url_for('utils.cdn_band_picture', filename=artist.band_cover)
        else:
            # TODO What if there is no band cover known?
            temp.cover_img = None

        # Amount of songs
        # TODO Implement
        temp.amount_songs = 19

        # Amount of albums
        # TODO Implement
        temp.amount_albums = 3

        # TODO Make this a public function
        # /artist/gojira
        # /artist/the-chats
        # /artist/system-of-a-down

        # Make lowercase
        # replace spaces with -
        # TODO remove alot of weird characters
        name = artist.name
        safe_artist_name = (artist.name.replace(" ", "-").lower())

        temp.url_to_artist = url_for('artists.artist', arg_artist=safe_artist_name)

        # TODO implement
        url_to_albums = None

        # TODO implement
        url_to_songs = None

        # Add this collection to a list, so we can send it to the renderer.
        if DEBUG:
            print(f"artist_list :: temp object :: {temp}")
        artists_for_this_page.append(temp)

    return render_template('list_artist.html', title=title,artist_list=artists_for_this_page, paginate=artists_from_db)


############################################################
# Route for displaying a single artist
# TODO BASICS, REWRITE
############################################################
@bp_artists.route("/artist/<arg_artist>")
def artist(arg_artist):
    artist_object = db.session.query(Artist).filter(func.lower(Artist.name) == func.lower(arg_artist)).first()
    if artist_object is None:
        # trow 404
        return '404'
    print(artist_object)
    return render_template('artist.html', artist=artist_object)


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
    
    print(f'This{band_cover}')
        
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
        return new_artist.id





