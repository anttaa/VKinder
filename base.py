import sqlite3


class Database:
    def __init__(self, name):
        self.__dbname = name
        self.__conn = None
        self.__cursor = None
        self.__connect__()
        self.__create_db__()

    def __connect__(self):
        if self.__conn is None:
            self.__conn = sqlite3.connect(self.__dbname, isolation_level="IMMEDIATE")
            self.__conn.isolation_level = None
            self.__cursor = self.__conn.cursor()

    def __create_db__(self):
        # Таблица с профилями
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS profiles
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         vk_id integer,
                         first_name text NOT NULL,
                         last_name text,
                         age integer default -1,
                         sex integer default -1,
                         city text,
                         offset integer default 0,
                         token text,
                         photos text,
                         status integer default 1)
                     """
        )

        # # Таблица с фотками
        # self.__cursor.execute(
        #     """CREATE TABLE IF NOT EXISTS photos
        #                 (vkid integer,
        #                  link text NOT NULL)
        #              """
        # )

        # Таблица favorite
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS relationship
                        (vkid_profile integer,
                         vkid_candidate integer not null,
                         flag int default 2)
                     """
        )

    def profile_save(self, profile):
        try:
            if profile.id != -1:
                self.__cursor.execute(
                    """update profiles set first_name=?, last_name=?, age=?, sex=?, city=?, offset=?, photos=? where id=?""",
                    (
                        profile.first_name,
                        profile.last_name,
                        profile.age,
                        profile.sex,
                        profile.city,
                        int(profile.offset),
                        profile.photos,
                        profile.id,
                    ),
                )
            else:
                self.__cursor.execute(
                    """insert into profiles(vk_id, first_name, last_name, age, sex, city, photos, offset) values(?,?,?,?,?,?,?,?)""",
                    (
                        profile.vk_id,
                        profile.first_name,
                        profile.last_name,
                        profile.age,
                        profile.sex,
                        profile.city,
                        profile.photos,
                        int(profile.offset),
                    ),
                )
            self.__conn.commit()  # Сохраняем изменения
            if profile.id == -1:
                profile.id = self.__cursor.lastrowid
        except Exception as e:
            print("profile_save_error", e)
            return False

    def profile_load(self, vk_id):
        data = None
        try:
            self.__cursor.execute("""select * from profiles where vk_id=?""", (vk_id,))
            res = self.__cursor.fetchone()
            if res is not None:
                data = {
                    "id": res[0],
                    "vk_id": res[1],
                    "first_name": res[2],
                    "last_name": res[3],
                    "age": res[4],
                    "sex": res[5],
                    "city": res[6],
                    "offset": res[7],
                    "token": res[8] if res[8] is not None else -1,
                    "photos": res[9],
                }
        except Exception as e:
            print("profile_load", e)
        return data

    def candidates_save(
        self, profile, client, flag=2
    ):  # flag: 1 (favorite) или 2 (Nope)
        try:
            self.__cursor.execute(
                """insert into relationship(vkid_profile, vkid_candidate, flag) values(?,?,?)""",
                (
                    profile.vk_id,
                    client.vk_id,
                    flag,
                ),
            )
            self.__conn.commit()  # Сохраняем изменения
        except Exception as e:
            print("candidates_save", e)
            return False

    def candidates_check(self, profile, client):
        res = None
        try:
            self.__cursor.execute(
                """select * from relationship where vkid_profile=? and vkid_candidate=?""",
                (profile.vk_id, client.vk_id),
            )
            res = self.__cursor.fetchone()
        except Exception as e:
            print("profile_load", e)
        return res["flag"] if res is not None else None

    def favorite_load(self, profile, offset, limit=10):  # Возвращает список анкет
        data = []
        try:
            self.__cursor.execute(
                """select vk_id,first_name,last_name,photos from relationship as r left join profiles as p on (r.vkid_candidate=p.vk_id) where vkid_profile=? and flag=1 LIMIT ? OFFSET ?""",
                (profile.vk_id, int(limit), int(offset)),
            )
            for rec in self.__cursor.fetchall():
                data.append(
                    {
                        "vk_id": rec[0],
                        "first_name": rec[1],
                        "last_name": rec[2],
                        "photos": rec[3],
                    }
                )
        except Exception as e:
            print("favorite_load", e)
        return data

    def token_load(self, profile):
        res = None
        try:
            self.__cursor.execute(
                """select token from profiles where id=?""", (profile.id,)
            )
            res = self.__cursor.fetchone()

            if res is not None:
                res = res[0] if res[0] is not None else -1

        except Exception as e:
            print("token_load", e)
        return res if res is not None else -1

    def token_save(self, vk_id, token):
        self.__cursor.execute(
            "update profiles set token=? where vk_id=?", (token, vk_id)
        )
