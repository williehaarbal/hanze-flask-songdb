import sqlite3
import os
from app.color import bcol

class DB(object):
    root_folder = None
    database_folder = 'database'
    database = None
    complete_database_path = None
    active_connection = None
    cursor = None


    def __init__(self, database) -> None:
        print(f'{bcol.CYAN}{"#" * 40}{bcol.END}')
        print(f'{bcol.CYAN}Opening database connection{bcol.END}')

        # Get relative path to find current workspace
        self.root_folder = os.getcwd()
        print(f"{bcol.CYAN}Root folder: {self.root_folder}")
        print(f"Database folder: {self.database_folder}")
        self.database = database
        print(f"database: {self.database}")
        self.complete_database_path = os.path.join(self.root_folder, self.database_folder, self.database)
        print(f"Complete path to DB: {self.complete_database_path}")
        print(f'{bcol.CYAN}{"#" * 40}{bcol.END}')

        try:
            self.active_connection = sqlite3.connect(self.complete_database_path)
        except Exception as e:
            raise FileNotFoundError(f"{bcol.FAIL}ERROR: Could not find '{self.database}', please check config.{bcol.END}")
        
        try:
            self.cursor = self.active_connection.cursor()
        except Exception as e:
            raise Exception(f"{bcol.FAIL}ERROR: Could not create cursor.{bcol.END}")

            

    # # CREATE DATABASE CONNECTION
    # @staticmethod
    # def open_db_con(database) -> object:
    #     try:
    #         db = DB(database)
    #     except FileNotFoundError as FNFE:
    #         print(FNFE)
    #         # If no database connection could be made, return None
    #         return None
    #     except Exception as e:
    #         print(f'CRIT ERROR: {e}')
    #         return None
    #     return DB(database)

    def exe(self, query):
        print(f'{bcol.WARN}{"#" * 40}{bcol.END}')
        print(f'{bcol.WARN}Executing query:{bcol.END}')
        print(f'{bcol.WARN}{query}{bcol.END}')
        print(f'{bcol.WARN}{"#" * 40}{bcol.END}')
        try:
            self.cursor.execute(query)
        except Exception as e:
            print(f'{bcol.FAIL}ERROR: (db.exe) Failed to execute query -> "{e}{bcol.END}"')

    def f_one(self):
        return self.cursor.fetchone()
    
    def f_one_untuppled(self):
        if self.cursor.fetchone is not None:
            return str(self.cursor.fetchone()[0])
        else:
            return None
        

    def commit(self):
        self.active_connection.commit()

    def close(self):
        self.active_connection.close()
    
    def f_all(self):
        return self.cursor.fetchall()
    
