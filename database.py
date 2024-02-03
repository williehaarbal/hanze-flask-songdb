import sqlite3

database_name = 'sqlite_db.db'
database_path = None

con = sqlite3.connect(database_name)
cur = con.cursor()

query = """
CREATE TABLE song(title, year, score);
"""

cur.execute(query)

