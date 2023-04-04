import sqlite3


class Database:

    def __init__(self, name):
        self.dbname = name
        self.conn = None
        self.cursor = None
        self.__connect__()
        self.__create_db__()

    def __connect__(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.dbname)
            self.cursor = self.conn.cursor()

    def __create_db__(self):
        # Таблица с профилями
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                        (vkid INTEGER PRIMARY KEY,
                         first_name text NOT NULL,
                         last_name text,
                         birthday datetime,
                         sex integer,
                         city text,
                         offset integer default 0,
                         token text,
                         status INTEGER default 1)
                     """)

        # Таблица с фотками
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS photo
                        (vkid integer,
                         link text NOT NULL)
                     """)

        # Таблица favorite
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS favorite
                        (vkid integer,
                         vkid_candidate integer not null)
                     """)

    
