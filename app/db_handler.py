import sqlite3
import os

class DB(object):
    runtime_relative_path = None
    database_name = 'database/main.db'
    active_connection = None
    cursor = None


    def __init__(self) -> None:
        
        self.runtime_relative_path = os.getcwd()
        print(self.runtime_relative_path)
        self.active_connection = sqlite3.connect(self.database_name)
        self.cursor = self.active_connection.cursor()


    def exe(self, query):

        self.cursor.execute(query)

    def commit(self):
        self.active_connection.commit()

    def close(self):
        self.active_connection.close()

    def get_dir(self) -> str:
        return self.runtime_relative_path
    
    def fall(self):
        return self.cursor.fetchall()