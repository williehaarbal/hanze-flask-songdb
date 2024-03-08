############################################################
# FUNC
############################################################
def generate_song_list():
    """
    :param int page: The current page of pagination
    :rtype str
    """
    

    
    # Pagination settings
    page = request.args.get('page', 1, type=int)
    entries_per_page = 10

    # Cannot show page if visitor is logged in.
    if not current_user.is_authenticated:
        flash('Please login to start using this functionality.')
        return redirect(url_for('users.login'))
    
    
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
    
    # Get a list up to 10 songs (by paginate & that are 'alive' / not deleted).
    songs_retrieved_from_database = Song.query.filter(Song.alive==True).paginate(page=page, per_page=entries_per_page)

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
        current_page = request.url
        
        # URL to like
        # Passes the current page as a argument
        song_object.url_to_like = f'/song/{song_object.id}/like?current_page={current_page}'
        # URL to unlike
        # Passes the current page as a argument
        song_object.url_to_unlike = f'/song/{song_object.id}/unlike?current_page={current_page}'

        song_for_display.append(song_object)
        
        
    for i in song_for_display:
        p_note(i.favorite)

    return render_template('songs.html', title=title, songs=song_for_display, paginate=songs_retrieved_from_database)

############################################################
# REDIRECT :: Like song by user
############################################################
@bp_songs.route("/song/<song_id>/like", methods=['GET','POST'])
def action_like_song(song_id):
    current_page = request.args.get('current_page', None)
    like = UsersLikesSongs()
    like.user_id = int(current_user.id)
    like.song_id = int(song_id)
    db.session.add(like)
    db.session.commit()
    return redirect(current_page)

############################################################
# REDIRECT :: Unlike song by user
############################################################
@bp_songs.route("/song/<song_id>/unlike", methods=['GET','POST'])
def action_unlike_song(song_id):
    current_page = request.args.get('current_page', None)
    response = UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song_id).all()
    for r in response:
        db.session.delete(r)
    db.session.commit()
    return redirect(current_page)

############################################################
# ROUTE :: Song
############################################################
@bp_songs.route('/song/<song_id>', methods=['GET', 'POST'])
def song(song_id):

    # If the current user isn't authenticated (anonymouse), then redirect him/her to login page.
    if not current_user.is_authenticated:
        flash('Please login to access songs...')
        return redirect(url_for('users.login'))

    # Get some object from database
    song_retrieved_from_database = Song.query.filter_by(id=song_id).first()
    # If song not found, throw an error
    # TODO Is this proper error handing here?
    if song_retrieved_from_database is None:
        abort(500)

    # GENERAL :: title
    title = f'MusicDB :: {song_retrieved_from_database.title}'

    # A class that acts as a container to hold info over a song (single object = single song)
    class song_container():
        # General
        title = None
        artist = None
        album = None
        length = None
        favorite = None
        
        # CDN
        cdn_song_file = None
        cdn_song_cover = None
        cdn_artist_country_flag = None
        
        # URLs
        url_to_artist = None
        url_to_album = None
        url_to_edit = None
        url_to_like = None
        url_to_unlike = None
        
    # Get title
    song_container.title = song_retrieved_from_database.title
    # Get artist
    if song_retrieved_from_database.artist:
        song_container.artist = song_retrieved_from_database.artist.name
    # Get album
    if song_retrieved_from_database.album:
        song_container.album = song_retrieved_from_database.album.name
    # Get length
    if song_retrieved_from_database.length_in_sec:
        song_container.length = sec_to_str(song_retrieved_from_database.length_in_sec)
        
        
    # Is favorite
    if UsersLikesSongs.query.filter_by(user_id=current_user.id, song_id=song_retrieved_from_database.id).first() is None:
        song_container.favorite = False
    else:
        song_container.favorite = True
    
    # CDN
    # Get song cover
    if song_retrieved_from_database.file_cover:
        song_container.cdn_song_icon = url_for('utils.cdn_song_icons', filename=song_retrieved_from_database.file_cover)
    # Get music file
    if song_retrieved_from_database.file_name:
        song_container.cdn_song_file = url_for('utils.cdn_songs', filename=song_retrieved_from_database.file_name)
    # Get country flag
    if song_retrieved_from_database.artist.country:
        p_note('trigger')
        song_container.cdn_artist_country_flag = url_for('utils.cdn_flags', long_country_name=song_retrieved_from_database.artist.country)
    else:
        song_container.cdn_artist_country_flag = url_for('utils.cdn_flags', long_country_name='world')
    # URL to edit
    song_container.url_to_edit = f'/song/{song_retrieved_from_database.id}/edit'
    # URL to artist
    song_container.url_to_artist = f'/artist/{song_retrieved_from_database.artist_id}'
    # URL to album
    song_container.url_to_album = f'/album/{song_retrieved_from_database.album_id}'
    
    # Get the URL of the current page. If a user 'likes' or 'unlikes' a song, it calls a route that handles liking/unliking. Then redirects to the page it was already on. (refreshes for updates page.) Very hacky. Works somehow like a charm.
    # Done this way so you can like/unlike from multiple different pages.
    current_page = request.url
    
    # URL to like
    # Passes the current page as a argument
    song_container.url_to_like = f'/song/{song_retrieved_from_database.id}/like?current_page={current_page}'
    # URL to unlike
    # Passes the current page as a argument
    song_container.url_to_unlike = f'/song/{song_retrieved_from_database.id}/unlike?current_page={current_page}'

    return render_template('song.html', title=title, song=song_container)