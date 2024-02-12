
import math
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import render_template
from flask_login import current_user
import werkzeug
from musicdb.bp_artists.routes import parse_artist_url
from musicdb import db, app
from musicdb.general import p_err

from musicdb.models import Artist, Song

bp_main = Blueprint('main', __name__)


@bp_main.route("/")
@bp_main.route("/home")
def home():
    title = 'MusicDB :: home'
    page = request.args.get('page', 1, type=int)
    entries_per_page = 3

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
    
    songs_from_db = Song.query.filter_by().order_by(Song.created_at.desc()).paginate(page=page, per_page=entries_per_page)
    p_err(songs_from_db)

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

        # TODO implement favs
        temp.is_favorite = None

        # CDN
        if song.file_cover:
            temp.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song.file_cover)
        if song.file_name:
            temp.cdn_song_file = url_for('utils.cdn_songs', filename=song.file_name)

        # TODO implement song page
        temp.url_to_song = None
        # TODO implement album page
        temp.url_to_album = None
        temp.url_to_artist = parse_artist_url(song.artist)

        song_for_display.append(temp)

    return render_template('home.html', title=title, songs=song_for_display, paginate=songs_from_db)


############################################################
# Time in sec represented in a string format
############################################################
def sec_to_str(time: int) -> str:
    if time == -1:
        return 'E:RR'
    
    sec = time % 60
    sec = math.floor(sec)
    sec = str(sec).zfill(2)
    min = math.floor(time / 60)



    time = 5
    return f"{min}:{sec}"



# app name 
@bp_main.route('/404')
@bp_main.errorhandler(404) 
  
# inbuilt function which takes error as parameter 
def not_found(): 
  
# defining function 
  return render_template("404.html")

@bp_main.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request():
    return 'bad request!', 400
