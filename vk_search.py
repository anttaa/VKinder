import time
import requests
from datetime import date, datetime


class VkSearch:
    url = 'https://api.vk.com/method'

    def __init__(self, vk_id: int, bdate: str, sex: int, city_id: str, db_session, params: dict):
        self.vk_id = vk_id
        self.age_from = self.calculate_age(bdate) - 2
        self.age_to = self.age_from + 4
        self.sex = 1 if sex == 2 else 2
        self.status = 1
        self.city_id = city_id
        self.has_photo = 1
        self.offset = 0

        self.db_session = db_session
        self.params = params

    def calculate_age(self, bdate):
        bdate = datetime.strptime(bdate, '%d.%m.%Y')
        today = date.today()
        age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        return age

    def __get_photo__(self, vk_id):
        params = {
            'owner_id': vk_id,
            'album_id': 'profile',
            'extended': 1
        }
        time.sleep(0.5)
        return requests.get(f'{self.url}/photos.get', params={**self.params, **params}).json()['response']

    def __search__(self, offset):
        params = {
            'age_from': self.age_from,
            'age_to': self.age_to,
            'sex': self.sex,
            'city_id': self.city_id,
            'status': self.status,
            'has_photo': self.has_photo,
            'fields': 'sex,city,bdate,screen_name,photo_id',
            'offset': offset,
            'count': 1
        }
        time.sleep(0.5)
        return requests.get(f'{self.url}/users.search', params={**self.params, **params}).json()['response']['items'][0]

    def next(self, offset):
        while True:
            result = self.__search__(self.offset)
            # print(result)
            self.offset += 1
            # print(self.offset)
            if result['is_closed']:
                continue
            # result['photos'] = self.__get_photo__(result['response']['items'][0]['id'])['response']['count']
            result['photos'] = self.__get_photo__(result['id'])['count']
            break
        return result
