import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

from DB.create_table import create_tables, Profiles, Relationship, Settings
from DB.settings import db_name, db_password, db_users

DSN = f"postgresql://{db_users}:{db_password}@localhost:5432/{db_name}"
engine = sq.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Database:
    def profile_save(self, profile):
        if (
            session.query(Profiles.filter(Profiles.vk_id == profile.vk_id)).first()
            is None
        ):
            # list_id_vk = []
            # for item in profile:
            #     list_id_vk.append(item[0])
            # if vk_ids not in list_id_vk:
            session.add(
                Profiles(
                    profile.vk_id,
                    profile.first_name,
                    profile.last_name,
                    profile.age,
                    profile.sex,
                    profile.city,
                    profile.photos,
                )
            )
        else:
            session.query(
                Profiles.filter(Profiles.vk_id == profile.vk_id)
                .first()
                .update(
                    profile.vk_id,
                    profile.first_name,
                    profile.last_name,
                    profile.age,
                    profile.sex,
                    profile.city,
                    profile.photos,
                    synchronize_session="fetch",
                )
            )
        session.commit()

    def profile_load(self, vk_ids: int):
        data = None
        res = session.query(Profiles.filter(Profiles.vk_id == vk_ids)).first()
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
                # "token": res[8] if res[8] is not None else -1,
                "photos": res[8],
            }
        return data

    def profile_del(self, profile):
        pass
        # self.cursor.execute("""delete from profiles where vk_id=?""", (profile.vk_id,))
        # self.cursor.execute("""delete from relationship where vkid_profile=?""", (profile.vk_id,))
        # self.cursor.execute("""delete from settings where vk_id=?""", (profile.vk_id,))
        # self.conn.commit()  # Сохраняем изменения

    def offset_load(self, profile):
        res = (
            session.query(Settings.offset)
            .filter(Settings.vkid_profile == profile.vk_id)
            .first()
        )
        return res[0] if res is not None else None
    def offset_save(self, profile, value):
        session.query(Settings.offset).filter(
            Settings.vkid_profile == profile.vk_id
        ).first().update(Settings.offset == value)

    def candidates_save(self, profile, client, flag=2):
        # self.profile = (
        #     session.query(Relationship)
        #     .filter(Relationship.vkid_profile == profile.vk_id)
        #     .filter(Relationship.vkid_candidate == client.vk_id)
        #     .all()
        # )
        # list_candidates = []
        # for favorite in profile:
        #     list_candidates.append(favorite[0])
        # if vk_ids not in list_candidates:
        if (
            session.query(Relationship)
            .filter(Relationship.vkid_profile == profile.vk_id)
            .filter(Relationship.vkid_candidate == client.vk_id)
            .all()
        ):
            session.add(
                Relationship(profile.vk_id, client.vk_id, flag)
            )

    def candidates_check(self, profile, client):
        res = (
            session.query(Relationship)
            # .filter(Relationship.flag)
            .filter(Relationship.vkid_candidate == profile.vk_id)
            .filter(Relationship.vkid_profile == client.vk_id)
            .first()
        )
        if res is None:
            return None
        else:
            return res.flag
        # if flag.flag == 0:
        #     flag.update(f"{Relationship.flag: 1}")
        # else:
        #     flag.update(f"{Relationship.flag: 2}")

    def candidates_del(self, vk_ids: int, profile, client):
        pass

    # def add_settings(self, vk_ids: int, profile, token):
    #     self.profile = (
    #         session.query(Settings.token).filter(Settings.vkid_profile == vk_ids).all()
    #     )
    #     set_list = []
    #     for item in profile:
    #         set_list.append(item[0])
    #         if token not in set_list:
    #             session.add(
    #                 Settings(profile.vkid_profile, profile.token, profile.offset)
    #             )

    def favorite_load(self, profile, offset, limit=10):
        data = []
        result = (
            session.query(
                Relationship.vkid_profile,
                Profiles.first_name,
                Profiles.last_name,
                Profiles.photos,
            )
            .join(Profiles)
            .join(Relationship)
            .filter(Relationship.vkid_profile == profile.vk_id)
            .filter(Relationship.flag == 1)
            .limit(limit)
            .offset(offset)
            .all()
        )
        for item in result:
            data.append(
                {
                    "vk_id": item[0],
                    "first_name": item[1],
                    "last_name": item[2],
                    "photos": item[3],
                }
            )
            return data

    def token_load(self, profile):
        res = (
            session.query(Settings.token)
            .filter(Settings.vkid_profile == profile.vk_id)
            .first()
        )
        return res[0] if res is not None else None

    def token_save(self, profile, token):
        session.query(Settings.token).filter(
            Settings.vkid_profile == profile.vk_id
        ).first().update(Settings.token == token)
