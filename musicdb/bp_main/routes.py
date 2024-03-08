
import math
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import render_template
from flask_login import current_user
import werkzeug
from musicdb.bp_artists.routes import parse_artist_url
from musicdb import db, app
from musicdb.bp_utils.func import sec_to_str
from musicdb.general import p_err

from musicdb.models import Artist, Song

bp_main = Blueprint('main', __name__)

############################################################
# ROUTE :: FRONT PAGE
# STATUS :: GOOD ENOUGH
############################################################
@bp_main.route("/")
@bp_main.route("/front")
@bp_main.route("/home") # Legacy / should be replaced by '/front' in future.
def front_page() -> str:
    """
    Route for front page.
    """

    # GENERAL :: page title
    title = 'MusicDB :: front page'

    # Pagination for 'latest uploaded songs'
    # Gets the first page of all uploaded songs, ordered by date, and get only the first 3 (on page 1)
    page = request.args.get('page', 1, type=int)
    entries_per_page = 3


    # A class that acts as a container to hold info over a song (single object = single song)
    class Song_info_container():
        # General
        id = None
        title = None
        album = None
        artist = None
        length = None
        favorite = False # TODO Not implemented yet
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


    # Holds all the song objects in an list that will be able to be looped over with Flask render_template.
    songs_for_display = []

    # From the database; get the last three songs uploaded by datetime.
    songs_retrieved_from_database = Song.query.filter_by().order_by(Song.created_at.desc()).paginate(page=page, per_page=entries_per_page)

    # The reason why we don't directly pass the song objects retrieved from the database to Flask render_template is because some information is missing. Also URL's for CDN and redirecting is easier handeld in Python then in-html Flask {{....}}. We get lacking formation below. Then finally add it the the list (songs_for_display) we made earlier.
    for song in songs_retrieved_from_database:

        song_container = Song_info_container()

        #GENERAL
        song_container.id = song.id
        song_container.title = song.title
        
        # Check if the songs has a connected album. (Some songs aren't part of an album)
        if song.album is not None:
            song_container.album = song.album.name
        else:
            song_container.album = "Unknown album"
            
        # Check if an artist is known for the song. (This could be missing)
        if song.artist is not None:
            song_container.artist = song.artist.name
        else:
            song_container.artist = "Unknown artist"
            
        #  Get the length in seconds of a song.
        song_container.length = sec_to_str(song.length_in_sec)

        # Check if song is favorited by the current user
        # Check in table 'UsersLikesSongs' if the combination of song & current user exists
        # TODO implement favs
        song_container.is_favorite = False

        # CDN
        # Uses from the utils blueprint the CDN functions to determine the relative paths of files.
        if song.file_cover:
            song_container.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
            song_container.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)
            
            
        # URLs
        # TODO use url_for instead of f-strings
        # URL to song
        song_container.url_to_song = f'/song/{song.id}'
        
        # URL to album (if part of album)
        if song.album_id:
            song_container.url_to_album = f'/album/{song.album_id}'
        else:
            song_container.url_to_album = None
        # URL to artist (if artist info exists)
        if song.artist_id:
            song_container.url_to_artist = f'/artist/{song.artist_id}'
        else:
            song_container.url_to_album = None

        
        # Add the song container to the list of songs that will be displayed on the rendered page.
        songs_for_display.append(song_container)

    return render_template('home.html', title=title, songs=songs_for_display)

