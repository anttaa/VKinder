import sqlite3
import datetime


class Database:
    def __init__(self, name):
        self.dbname = name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_db()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.dbname, isolation_level="IMMEDIATE")
            self.conn.isolation_level = None
            self.cursor = self.conn.cursor()

    def create_db(self):
        # Таблица с профилями
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS profiles
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         vk_id integer,
                         first_name text NOT NULL,
                         last_name text,
                         age integer default -1,
                         sex integer default -1,
                         city integer default -1,
                         photos text,
                         dt_update integer)
                     """
        )

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS settings
                        (vk_id integer PRIMARY KEY,
                         offset integer default 0,
                         token text)
                     """
        )

        # Таблица favorite
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS relationship
                        (vkid_profile integer,
                         vkid_candidate integer not null,
                         flag int default 2)
                     """
        )

    def profile_save(self, profile):
        if profile.id is not None:
            self.cursor.execute(
                """update profiles set first_name=?, last_name=?, age=?, sex=?, city=?, photos=?, dt_update=? where id=?""",
                (
                    profile.first_name,
                    profile.last_name,
                    profile.age,
                    profile.sex,
                    profile.city,
                    profile.photos,
                    datetime.datetime.now(),
                    profile.id,
                ),
            )
        else:
            self.cursor.execute(
                """insert into profiles(vk_id, first_name, last_name, age, sex, city, photos, dt_update) values(?,?,?,?,?,?,?,?)""",
                (
                    profile.vk_id,
                    profile.first_name,
                    profile.last_name,
                    profile.age,
                    profile.sex,
                    profile.city,
                    profile.photos,
                    datetime.datetime.now(),
                ),
            )
            self.cursor.execute(
                """insert into settings(vk_id) values(?)""",
                (
                    profile.vk_id,
                ),
            )
        self.conn.commit()  # Сохраняем изменения
        if profile.id is None:
            profile.id = self.cursor.lastrowid

    def profile_load(self, vk_id):
        data = None
        self.cursor.execute("""select * from profiles where vk_id=?""", (vk_id,))
        res = self.cursor.fetchone()
        if res is not None:
            data = {
                "id": res[0],
                "vk_id": res[1],
                "first_name": res[2],
                "last_name": res[3],
                "age": res[4] if res[4] != -1 else None,
                "sex": res[5] if res[5] != -1 else None,
                "city": res[6] if res[6] != -1 else None,
                "photos": res[7],
                "dt_update": res[8] if res[8] != -1 else None
            }
        return data

    def profile_del(self, profile):
        self.cursor.execute("""delete from profiles where vk_id=?""", (profile.vk_id,))
        self.cursor.execute("""delete from relationship where vkid_profile=?""", (profile.vk_id,))
        self.cursor.execute("""delete from settings where vk_id=?""", (profile.vk_id,))
        self.conn.commit()  # Сохраняем изменения

    def token_load(self, profile):
        self.cursor.execute(
            """select token from settings where vk_id=?""", (profile.vk_id,)
        )
        res = self.cursor.fetchone()
        return res[0] if res is not None else None

    def token_save(self, profile, value):
        self.cursor.execute('select * from settings where vk_id=?', (profile.vk_id,))
        res = self.cursor.fetchone()
        if res is None:
            self.cursor.execute(
                "insert settings(token) values(?)", (value,)
            )
        else:
            self.cursor.execute(
                "update settings set token=? where vk_id=?", (value, profile.vk_id,)
            )
        self.conn.commit()  # Сохраняем изменения

    def offset_load(self, profile):
        self.cursor.execute(
            """select offset from settings where vk_id=?""", (profile.vk_id,)
        )
        res = self.cursor.fetchone()
        return res[0] if res is not None else None

    def offset_save(self, profile, value):
        self.cursor.execute('select * from settings where vk_id=?', (profile.vk_id,))
        res = self.cursor.fetchone()
        if res is None:
            self.cursor.execute(
                "insert settings(token) values(?)", (value)
            )
        else:
            self.cursor.execute(
                "update settings set token=? where vk_id=?", (value, profile.vk_id,)
            )
        self.conn.commit()  # Сохраняем изменения

    def candidates_save(
        self, profile, client, flag=2
    ):  # flag: 1 (favorite) или 2 (Nope)
        self.cursor.execute(
            """insert into relationship(vkid_profile, vkid_candidate, flag) values(?,?,?)""",
            (
                profile.vk_id,
                client.vk_id,
                flag,
            ),
        )
        self.conn.commit()  # Сохраняем изменения

    def candidates_check(self, profile, client):
        self.cursor.execute(
            """select * from relationship where vkid_profile=? and vkid_candidate=?""",
            (profile.vk_id, client.vk_id),
        )
        res = self.cursor.fetchone()
        return res[2] if res is not None else None

    def candidates_del(self, profile, vk_id):  # flag: 1 (favorite) или 2 (Nope)
        self.cursor.execute(
            """update relationship set flag=2 where vkid_profile=? and vkid_candidate=?""",
            (
                profile.vk_id,
                vk_id,
            ),
        )

    def favorite_load(self, profile, offset, limit=10):  # Возвращает список анкет
        data = []
        self.cursor.execute(
            """select vk_id,first_name,last_name,photos from relationship as r left join profiles as p on (r.vkid_candidate=p.vk_id) where vkid_profile=? and flag=1 LIMIT ? OFFSET ?""",
            (profile.vk_id, int(limit), int(offset)),
        )
        for rec in self.cursor.fetchall():
            data.append(
                {
                    "vk_id": rec[0],
                    "first_name": rec[1],
                    "last_name": rec[2],
                    "photos": rec[3],
                }
            )
        return data
