# STATIC DATA :: SONGS ICONS
# CDN path is what user sees in browser!
from flask import Blueprint, send_from_directory
from musicdb import app

bp_utils = Blueprint('utils', __name__)


@bp_utils.route('/cdn/i/<path:filename>')
def cdn_song_icons(filename):
    return send_from_directory(app.config['SONG_COVERS_ICON'], filename)

@bp_utils.route('/cdn/ib/<path:filename>')
def cdn_song_big(filename):
    return send_from_directory(app.config['SONG_COVER'], filename)

# STATIC DATA :: SONGS
# CDN path is what user sees in browser!
@bp_utils.route('/cdn/s/<path:filename>')
def cdn_songs(filename):
    return send_from_directory(app.config['SONG_FOLDER'], filename)

# STATIC DATA :: SONGS
# CDN path is what user sees in browser!
@bp_utils.route('/cdn/pp/<path:filename>')
def cdn_profile_picture(filename):
    return send_from_directory(app.config['PROFILE_PICTURE'], filename)

# STATIC DATA :: SONGS
# CDN path is what user sees in browser!
@bp_utils.route('/cdn/ac/<path:filename>')
def cdn_band_picture(filename):
    return send_from_directory(app.config['BAND_COVER'], filename)


# STATIC DATA :: SONGS
# CDN path is what user sees in browser!
@bp_utils.route('/cdn/st/<path:filename>')
def cdn_flags(filename):
    return send_from_directory(app.static_folder, f'flags/{filename}')
