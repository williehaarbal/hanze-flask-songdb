############################################################
# FUNC :: Generate album list
############################################################

from flask import url_for


def generate_album_list(page: int, entries_per_page: int, albums_retrieved_from_database: object, current_page: str):
    class album_info_container():
        # General
        name = None
        artist = None

        # URLs
        url_to_album = None
        url_to_artist = None
        
        # CDN
        album_cover = None
        
    
    # List with album (objects) used by flask to iterate over.
    albums_for_display = []

    for album in albums_retrieved_from_database:
        album_object = album_info_container()

        # Name
        album_object.name = album.name
        # Artist
        if album.artist:
            album_object.artist = album.artist.name
        else:
            album_object.artist = 'Unknown artist'
        
        # URL
        # URL_to_album
        album_object.url_to_album = f'/album/{album.id}'
        # url_to_artist
        if album.artist_id:
            album_object.url_to_artist = f'/artist/{album.artist_id}'
        else:
            album_object.url_to_artist = None
        
        # CDN
        # album_cover
        if album.album_cover:
            album_object.album_cover = url_for('utils.cdn_song_big', filename=album.album_cover)
        else:
            album_object.album_cover = None

        # Add album to list
        albums_for_display.append(album_object)    

    return albums_for_display, albums_retrieved_from_database