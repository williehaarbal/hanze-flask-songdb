
-- DROP TABLE songs
DROP TABLE songs;

-- INSERT INTO songs

INSERT INTO songs(song_name, artist, album, extention, song_length, path_album_image, path_file, created_at)
VALUES(
'Nummertje',
'William',
'VAAG ALBUM',
'mp3',
300,
'some_path',
'some_path',
datetime('now')
);


DELETE FROM songs;

-- SELECT SONGS BY SESSION UPLOAD ID

SELECT id, upload_session, song_name, artist, album, path_album_image, extention, song_length FROM songs
WHERE songs.upload_session;

