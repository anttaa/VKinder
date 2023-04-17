import requests
from handler.tools import profile_vk_check
from time import sleep


class VkUser:
    url = "https://api.vk.com/method"

    def __init__(self, db_session, vk_id, token, version="5.131"):
        self.token = token
        self.db_session = db_session
        self.params = {"access_token": token, "v": version}
        self.id = -1
        self.vk_id = vk_id
        self.first_name = ""
        self.last_name = ""
        self.age = None
        self.sex = None
        self.city = None
        self.offset = 0
        self.photos = ""
        self.dt_update = None

        self.load()
        self.token = self.db_session.token_load(self)
        self.offset = self.db_session.offset_load(self)

    def get_offset(self):
        self.offset += 1
        self.save()
        return self.offset

    def load(self):
        profile = self.db_session.profile_load(
            self.vk_id
        )  # Проверяем наличие в базе
        if profile is None:
            params = {
                "user_ids": self.vk_id,
                "fields": "bdate,city,sex,deactivated,home_town",
            }
            res = requests.get(
                f"{self.url}/users.get", params={**self.params, **params}
            ).json()
            if "error" in res:
                return None
            profile = profile_vk_check(res["response"][0])
            profile["id"] = None
            profile["photos"] = ""
            profile["dt_update"] = None
        self.id = profile["id"]
        self.token = None
        self.first_name = profile["first_name"]
        self.last_name = profile["last_name"]
        self.age = profile["age"]
        self.sex = profile["sex"]
        self.city = profile["city"]
        self.photos = profile["photos"]
        self.dt_update = profile["dt_update"]

    def save(self):
        self.db_session.profile_save(self)  # Сохраняем профиль полученный из ВК

    def photo_update(self):
        params = {"owner_id": self.vk_id, "photo_sizes": 0, "extended": 1}
        sleep(0.5)
        lres = {}
        res = requests.get(
            f"{self.url}/photos.getAll", params={**self.params, **params}
        ).json()
        for photo in res["response"]["items"]:
            if photo["id"] not in lres:
                lres[photo["likes"]["count"]] = photo["id"]
        self.photos = ",".join(
            [
                f"photo{self.vk_id}_{lres[photo_id]}"
                for photo_id in sorted(lres, reverse=True)[:3]
            ]
        )
        self.save()

    def delete(self):
        self.db_session.profile_del(self)
