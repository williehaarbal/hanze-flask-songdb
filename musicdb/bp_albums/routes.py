from musicdb.bp_main.routes import sec_to_str
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

    if not current_user.is_authenticated:
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))
    page = request.args.get('page', 1, type=int)
    entries_per_page = 8

    shown_album = []
    class Temp_album():
        name = None
        album_cover = None
        artist = None

        # URLS

        url_to_album = None
        url_to_artist = None

        def __repr__(self) -> str:
            return f"TEMP ALBUM OBJECT :: name: {self.name}, album_cover: {self.album_cover}, artist: {self.artist} "

    # all_albums_from_db = Album.query.paginate(page=page, per_page=entries_per_page)
    
    all_albums_from_db = db.session.scalars(db.select(Album)).all()


    for album in all_albums_from_db:
        temp = Temp_album()

        # Name
        temp.name = album.name
        p_note(dir(album))
        # album_cover
        if album.album_cover:
            temp.album_cover = url_for('utils.cdn_song_big', filename=album.album_cover)
        else:
            temp.album_cover = None

        # Artist
        find_artist = Artist.query.filter(Artist.id == Album.artist_id).first()

        if find_artist:
            temp.artist = find_artist.name
        else:
            temp.artist = None
        
        # URL_to_album
        temp.url_to_album = f'/album/{album.id}'

        # url_to_artist
        temp.url_to_artist = f'/artist/{find_artist.id}'

        shown_album.append(temp)    
        

    for i in shown_album:
        p_note(i)
    return render_template('albums.html', albums=shown_album)


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
def single_album(id):
    
    album_id = id
    
    # General page info
    title = 'MusicDB'
    
    if not current_user.is_authenticated:
        flash('Please login to start using this part of the website...')
        return redirect(url_for('users.login'))
    
    album_info = db.session.query(Album).filter(Album.id == album_id).first()
    
    class album():
        name = album_info.name
        artist = album_info.artist.name
        description = album_info.description
        album_cover = url_for('utils.cdn_album_cover', filename=album_info.album_cover)
    
    song_for_display = []
    class s():
        # General
        id = None
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
    
    songs_from_db = db.session.query(Song).filter(album_id == Song.album_id)

    for song in songs_from_db:
        temp = s()

        #GENERAL
        
        temp.id = song.id
        temp.title = song.title
        # TODO implement album
        temp.album = None
        temp.artist = db.session.query(Artist.name).filter(Artist.id == song.artist_id).first()
        if temp.artist:
            temp.artist = temp.artist[0]


        temp.length = sec_to_str(song.length_in_sec)

        p_err(dir(song))
        
        if song.album:
                if song.album.name:
                    temp.album = song.album.name
                else:
                    temp.song = None
        else:
            temp.song = None

        # TODO implement favs
        temp.is_favorite = None

        # CDN
        if song.file_cover:
            temp.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
            temp.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)

        # TODO implement song page
        temp.url_to_song = f'/song/{song.id}'

        # TODO implement album page
        if song.album_id:
            temp.url_to_album = f'/album/{song.album_id}'
        else:
            temp.url_to_album = None

        # Artist page
        if song.artist_id:
            temp.url_to_artist = f'/artist/{song.artist_id}'
        else:
            temp.url_to_artist = None

        song_for_display.append(temp)
    
    
    return render_template("album.html", album=album, songs=song_for_display)