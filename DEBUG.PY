from app.db_handler import DB
from app.sql.sql import *

db = DB()

db.exe(SQL_GET_SONGS_BY_UPLOAD_SESSION(8873815703479665648))

for row in db.fall():
    print(row[0])