import requests
from handler.tools import profile_vk_check
from time import sleep


class VkUser:
    url = "https://api.vk.com/method"

    def __init__(self, db_session, vk_id, token, version="5.131"):
        self.__token = token
        self.__db_session = db_session
        self.__params = {"access_token": token, "v": version}
        self.__id = -1
        self.__vk_id = vk_id
        self.__first_name = ""
        self.__last_name = ""
        self.__age = -1
        self.__sex = -1
        self.__city = -1
        self.__offset = 0
        self.__photos = ""

        self.__load()

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def vk_id(self):
        return self.__vk_id

    @vk_id.setter
    def vk_id(self, value):
        self.__vk_id = value

    @property
    def token(self):
        if self.__token == -1:
            self.__token = self.__db_session.token_load(self)
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        self.__first_name = value

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        self.__last_name = value

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):
        self.__age = value

    @property
    def sex(self):
        return self.__sex

    @sex.setter
    def sex(self, value):
        self.__sex = value

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, value):
        self.__city = value

    @property
    def photos(self):
        return self.__photos

    @property
    def offset(self):
        return self.__offset

    @offset.setter
    def offset(self, value):
        self.__offset = value

    def get_offset(self):
        self.offset += 1
        self.save()
        return self.offset

    def __load(self):
        try:
            profile = self.__db_session.profile_load(
                self.__vk_id
            )  # Проверяем наличие в базе
            if profile is None:
                params = {
                    "user_ids": self.__vk_id,
                    "fields": "bdate,city,sex,deactivated,home_town",
                }
                res = requests.get(
                    f"{self.url}/users.get", params={**self.__params, **params}
                ).json()
                if "error" in res:
                    return None
                profile = profile_vk_check(res["response"][0])
                profile["id"] = -1
                profile["token"] = -1
                profile["offset"] = 0
                profile["photos"] = ""
            self.__id = profile["id"]
            self.__first_name = profile["first_name"]
            self.__last_name = profile["last_name"]
            self.__age = profile["age"]
            self.__sex = profile["sex"]
            self.__city = profile["city"]
            self.__photos = profile["photos"]
            self.__token = profile["token"]
            self.__offset = profile["offset"]
        except Exception as e:
            print("vk_profile -> __load", e)
            return None

    def save(self):
        self.__db_session.profile_save(self)  # Сохраняем профиль полученный из ВК

    def photo_update(self):
        params = {"owner_id": self.__vk_id, "photo_sizes": 0, "extended": 1}
        sleep(0.5)
        lres = {}
        res = requests.get(
            f"{self.url}/photos.getAll", params={**self.__params, **params}
        ).json()
        for photo in res["response"]["items"]:
            if photo["id"] not in lres:
                lres[photo["likes"]["count"]] = photo["id"]
        self.__photos = ",".join(
            [
                f"photo{self.__vk_id}_{lres[photo_id]}"
                for photo_id in sorted(lres, reverse=True)[:3]
            ]
        )
        self.save()
