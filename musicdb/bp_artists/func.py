
from flask import url_for
from markupsafe import Markup
from musicdb.general import p_err
from musicdb.models import Album, Song
from musicdb.bp_utils.routes import cdn_flags

############################################################
# FUNC :: Generate artist list
############################################################
def generate_artist_list(page: int, entries_per_page: int, artists_retrieved_from_database: object, current_page: str):
    
    class Artist_info_container():
        # General
        id = None
        name = None
        country = None
        description = None
        amount_songs = None
        amount_albums = None
        
        # CDN
        # (These are 'links' the browser can interpret to get files likes images, the mp3s and suchs)
        cdn_flag = None
        cdn_cover_img = None

        # URLS
        # Links to other pages that relate to this song

        url_to_artist = None
        url_to_albums = None
        url_to_songs = None
        
    # Holds all the artist objects in an list that will be able to be looped over with Flask render_template.
    artist_for_display = []
    
    for artist in artists_retrieved_from_database:
        artist_object = Artist_info_container()

        # Get id
        artist_object.id = artist.id
        # Get name
        artist_object.name = artist.name
        # Get country & country icon
        if artist.country:
            artist_object.country = artist.country
            artist_object.cdn_flag = cdn_flags(long_country_name=artist.country)
        else:
            artist_object.country = None
            artist_object.cdn_flag = None
            
        # Get description
        artist_object.description = Markup(artist.description)

        # Get cover image
        if artist.band_cover:
            artist_object.cdn_cover_img = url_for('utils.cdn_band_picture', filename=artist.band_cover)
        else:
            artist_object.cdn_cover_img = None

        # Amount of songs
        artist_object.amount_songs = Song.query.filter(Song.artist_id == artist.id).count()
        # Amount of albums
        artist_object.amount_albums = Album.query.filter(Album.artist_id == artist.id).count()
        # <a href = {{ url_for('find_question' ,question_id=1) }}>Question 1</a>

        # Get URL to artist page
        artist_object.url_to_artist = url_for('artists.artist', id=artist.id)

        # Get URL to album page
        # artist_object.url_to_albums = url_for('albums.album', id=artist.album_id)

        # TODO implement
        url_to_songs = None

        artist_for_display.append(artist_object)

    return artist_for_display, artists_retrieved_from_database

############################################################
# FUNC :: Generate artist list
############################################################
def generate_artist_page(artist_database_object: object):
    
    class Artist_info_container():
        # General
        name = None
        id = None
        description = None

        # CDN
        band_cover = None
        flag_svg = None

    #Name
    Artist_info_container.name = artist_database_object.name
    
    # Id
    Artist_info_container.id = artist_database_object.id

    #Cover
    if artist_database_object.band_cover:
        Artist_info_container.band_cover = url_for('utils.cdn_band_picture', filename=artist_database_object.band_cover)
    else:
        Artist_info_container.band_cover = url_for('static', filename= 'img/unknown_band.jpg')

    # FLAG
    
    if artist_database_object.country and artist_database_object.country is not 'world':
        short = artist_database_object.country
        Artist_info_container.flag_svg = url_for('utils.cdn_flags', long_country_name=short)
    else:
        Artist_info_container.flag_svg = url_for('utils.cdn_flags', long_country_name=f'world')

    # Description
    
    Artist_info_container.description = Markup(artist_database_object.description)
    
    return Artist_info_container