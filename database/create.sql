-- EMPTY TABLES
DELETE FROM song_has_artists;
DELETE FROM artists;
DELETE FROM albums;
DELETE FROM users;
DELETE FROM songs;

-- DELETE TABLES
DROP TABLE song_has_artists;
DROP TABLE artists;
DROP TABLE albums;
DROP TABLE users;
DROP TABLE songs;

-- CREATE TABLES
CREATE TABLE IF NOT EXISTS users(
    -- Identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_static_id TEXT UNIQUE,

    -- Personalia
    name TEXT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    country_flag TEXT,
    confirmed INTEGER,
    loc_profile_pic TEXT,

    -- Security
    password TEXT,
    crypt_method TEXT,

    -- More
    admin INTEGER,
    active INTEGER,
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS albums(
    -- Identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_static_id TEXT UNIQUE,

    name TEXT,
    description TEXT,
    loc_album_cover TEXT,

    -- More
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS artists(
    -- Identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_static_id TEXT UNIQUE,

    name TEXT,
    description TEXT,
    country_flag TEXT,

    -- More
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS songs(
    -- Identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_static_id TEXT UNIQUE,

    -- GENERAL
    song_name TEXT NOT NULL,
    -- artist is N-N
    fk_album_id INTEGER,

    -- METADATA
    fk_user_id INTEGER,
    length_in_sec INTEGER,
    extension TEXT,
    
    -- FILES
    loc_song_cover TEXT,
    loc_file TEXT,
    loc_file_confirmed INTEGER,
    loc_short_clip TEXT,

    -- OTHER
    upload_session INTEGER,
    created_at DATETIME,
    FOREIGN KEY (fk_user_id) REFERENCES users(id),
    FOREIGN KEY (fk_album_id) REFERENCES albums(id)
);

CREATE TABLE IF NOT EXISTS song_has_artists(
    fk_song_id INTEGER,
    fk_artist_id INTEGER,
    FOREIGN KEY (fk_song_id) REFERENCES songs(id),
    FOREIGN KEY (fk_artist_id) REFERENCES artists(id)
);
