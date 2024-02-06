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

def SQL_INSERT_NEW_USER(user_static_id, name: str, username: str, password: str, crypt_method: str, email: str, confirmed_email: str, loc_profile_pic: str, country_flag: str, admin: str, active: str) -> str:
    return f"""

INSERT INTO users(user_static_id, name, username, password, crypt_method, email, confirmed_email, loc_profile_pic, country_flag, admin, active, created_at)
VALUES(
'{user_static_id}',
'{name}',
'{username}',
'{password}',
'{crypt_method}',
'{email}',
'{confirmed_email}',
'{loc_profile_pic}',
'{country_flag}',
'{admin}',
'{active}',
datetime('now')
);

""".format(user_static_id, name, username, password, crypt_method, email, confirmed_email, loc_profile_pic, country_flag, admin, active)



# CHECKED
def SQL_USERNAME_EXISTS(username: str) -> str:
    return f"""
SELECT
    CASE WHEN EXISTS 
    (
        SELECT * FROM users 
        WHERE lower(username) == lower('{username}')
    )
    THEN 'True'
    ELSE 'False'
    END;
    """.format(username = username)

# CHECKED
def SQL_CONFIRMED_EMAIL_EXISTS(email: str) -> str:
    return f"""
SELECT
    CASE WHEN EXISTS 
    (
        SELECT * FROM users 
        WHERE lower(email) == lower('{email}') AND confirmed_email == 'True'
    )
    THEN 'True'
    ELSE 'False'
    END;
    """.format(email = email)

def SQL_GET_HIGHEST_USER_ID() -> str:
    return f"""
    SELECT max(user_static_id)
    FROM users;
"""

# DEPRICATED
def SQL_VALIDATE_LOGIN(email: str, password) -> str:
    return f"""
    SELECT user_static_id
    FROM users
    WHERE email == '{email}' AND password == '{password}';

""".format(email, password)

def SQL_GET_PASSWORD_HASH_FOR_EMAIL(email: str) -> str:
    return f"""
    SELECT password
    FROM users
    WHERE email == '{email}' AND confirmed_email == 'False';
""".format(email)

def SQL_GET_USER_STATIC_ID_FOR_EMAIL(email: str) -> str:
    return f"""
    SELECT user_static_id
    FROM users
    WHERE email == '{email}' AND confirmed_email == 'False';
""".format(email)

def SQL_GET_USERNAME_FOR_EMAIL(email: str) -> str:
    return f"""
    SELECT username
    FROM users
    WHERE email == '{email}' AND confirmed_email == 'False';
""".format(email)


def SQL_GET_MOST_BY_USERNAME(username: str) -> str:
    return f"""
    SELECT name, email, confirmed_email, loc_profile_pic, country_flag, created_at, user_static_id
    FROM users
    WHERE username = '{username}';
""".format(username)
