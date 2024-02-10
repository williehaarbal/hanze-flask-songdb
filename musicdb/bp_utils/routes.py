# STATIC DATA :: SONGS ICONS
# CDN path is what user sees in browser!
from flask import Blueprint, send_from_directory
from musicdb import app

bp_utils = Blueprint('utils', __name__)


@bp_utils.route('/cdn/i/<path:filename>')
def cdn_icons(filename):
    return send_from_directory(app.config['SONG_COVERS_ICON'], filename)


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