############################################################
# FUNC :: Generate song list
############################################################
from flask import render_template, url_for
from flask_login import current_user
from musicdb.bp_utils.func import sec_to_str
from musicdb.models import UsersLikesSongs


def generate_song_list(page: int, entries_per_page: int, songs_retrieved_from_database: object, current_page: str):
    """
    :param int page: The current page of pagination
    :param int entries_per_page: amount of songs per page
    :param object songs_retrieved_from_database: List of songs retrieved from database
    :param str current_page: Used to generate some URL's
    :rtype str
    """

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
    
        
        # URL to like
        # Passes the current page as a argument
        song_object.url_to_like = f'/song/{song_object.id}/like?current_page={current_page}'
        # URL to unlike
        # Passes the current page as a argument
        song_object.url_to_unlike = f'/song/{song_object.id}/unlike?current_page={current_page}'

        song_for_display.append(song_object)

    return song_for_display, songs_retrieved_from_database
