def SQL_INSERT_INTO_SONG(song_name: str, artist: str, album: str, extention: str, song_length: int, path_album_image: str, path_file: str, upload_session: int) -> str:
    return f"""
    INSERT INTO songs(
        song_name,
        artist,
        album,
        extention,
        song_length,
        path_album_image,
        path_file,
        confirmed_stored,
        upload_session,
        created_at
    )
    VALUES
    (
        \"{song_name}\",
        \"{artist}\",
        \"{album}\",
        \"{extention}\",
        {song_length},
        \"{path_album_image}\",
        \"{path_file}\",
        0,
        \"{upload_session}\",
        datetime(\"now\")
    );
"""


def SQL_GET_SONGS_BY_UPLOAD_SESSION(upload_session: int) -> str:
    return f"""
        SELECT id, upload_session, song_name, artist, album, path_album_image, extention, song_length FROM songs
        WHERE songs.upload_session == {upload_session};
"""


def SQL_CHANGE_ELEMENT_BY_ID(id: int, what: str, value: str) -> str:

    return f"""
    UPDATE songs
    SET {what} = \"{value}\"
    WHERE id = {id};

"""