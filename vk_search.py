import time
import requests
from vk_profile import VkUser


class VkSearch:
    url = "https://api.vk.com/method"

    def __init__(self, profile, db_session):
        self.__params = {"access_token": profile.token, "v": "5.131"}
        self.__profile = profile
        self.__db_session = db_session

    def __search(self):
        try:
            params = {
                "age_from": self.__profile.age - 2,
                "age_to": self.__profile.age + 2,
                "sex": 1 if self.__profile.sex == 2 else 2,
                "city_id": self.__profile.city,
                "status": 1,
                "has_photo": 1,
                "offset": self.__profile.get_offset(),
                "count": 1,
            }
            time.sleep(0.5)
            response = requests.get(
                f"{self.url}/users.search", params={**self.__params, **params}
            ).json()
            return response["response"]["items"][0]
        except Exception as e:
            print("__search", e)

    def next(self):
        client = None
        if self.__params["access_token"] == -1:
            return client
        while True:
            try:
                result = self.__search()
                if result["is_closed"]:
                    continue
                try:
                    client = VkUser(
                        self.__db_session, result["id"], self.__params["access_token"]
                    )
                    client.photo_update()
                    if (
                        self.__db_session.candidates_check(self.__profile, client)
                        is not None
                    ):
                        continue
                except Exception as e:
                    print("next -> while -> VkUser", e)
                break
            except Exception as e:
                print("next -> while", e)
        return client
