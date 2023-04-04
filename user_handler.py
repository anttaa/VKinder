import json
import requests
import random

from vk_search import VkSearch

def make_button(label: str, payload: str, color: str = 'secondary') -> dict:
    return {
        'action': {
            'type': 'text',
            'payload': payload,
            'label': label
        },
        'color': color if color is not None else 'secondary'
    }


def make_keyboard(buttons: list, to_mes: bool = False) -> dict:
    keyboard = {'inline': to_mes, 'buttons': []}
    for level in buttons:
        btns = []
        for param in level:
            btns.append(make_button(param[0], param[1], param[2] if len(param) == 3 else None))
        keyboard['buttons'].append(btns)
    # print(keyboard)
    return keyboard


class UserHandler:
    url = 'https://api.vk.com/method'

    def __init__(self, db_session, group_id: int, version: str, token_group: str, token_search: str):
        self.db_session = db_session
        self.bots = {}
        self.group_id = group_id
        self.params_search = {'access_token': token_search}
        self.params = {
            'access_token': token_group,
            'v': version
        }

    def send_message(self, user_id: int, message: str, attachment: str = None, buttons: list = None, btn_in_mes: bool = False):
        # https://dev.vk.com/method/messages.send
        try:
            params = {
                'user_id': user_id,
                'peer_id': user_id,
                'message': message,
                'random_id': random.randint(1, 10000)
            }
            if attachment is not None:
                params['attachment'] = attachment

            if buttons is not None:
                params['keyboard'] = json.dumps(make_keyboard(buttons, btn_in_mes), ensure_ascii=False)

            # print('send_message:', params)
            response = requests.get(f'{self.url}/messages.send', params={**self.params, **params}).json()
            return response
        except Exception as e:
            print(f'Ошибка: {str(e)}')

    def get_profile(self, ids):
        try:
            params = {'user_ids': ids, 'fields': 'bdate,city,sex,deactivated'}
            res = requests.get(f'{self.url}/users.get', params={**self.params, **params}).json()
            if 'error' in res:
                # print('Ошибка: ', res['error']['error_msg'])
                return None
            return res['response'][0]
        except Exception as e:
            return None

    def reg_profile(self, vk_id):
        if vk_id not in self.bots:
            vk_profile = self.get_profile(vk_id)
            err_txt = ''
            if 'bdate' not in vk_profile:
                err_txt += 'Не удается определить Ваш возраст, так как скрыта дата рождения'
            if vk_profile['sex'] == 0:
                err_txt += 'Не удается определить Ваш пол'
            if len(err_txt) < 1:
                self.bots[vk_id] = VkSearch(vk_profile['id'],
                                            vk_profile['bdate'],
                                            vk_profile['sex'],
                                            vk_profile['city']['id'],
                                            self.db_session,
                                            {**self.params, **self.params_search})
                self.send_message(
                    vk_id,
                    'Вступительное слово',
                    None,
                    [
                        [
                            ['В избранное', '{"command":"to_favorite"}', 'primary'],
                            ['Следующий', '{"command":"next"}']
                        ],
                        [
                            ['Избранные', '{"command":"favorites"}']
                        ]
                    ]
                )
            else:
                self.send_message(vk_id, f'Есть ошибки: {err_txt}')
                return None
        return self.bots[vk_id]

    def get_long_poll_server(self, group_id): # Запрос сервера
        try:
            params = {'group_id': group_id}
            response = requests.get(f'{self.url}/groups.getLongPollServer', params={**self.params, **params}).json()
            return response
        except Exception as e:
            return None

    def reg_long_poll_server(self): # Запускаем сервер
        try:
            response = self.get_long_poll_server(self.group_id)
            if response is None:
                return
            ts = response['response']['ts']
            answer = True
            print('Сервис запущен')
            res = None
            while answer:
                try:
                    res = requests.get(f'{response["response"]["server"]}?act=a_check&key={response["response"]["key"]}&ts={ts}&wait=25').json()
                    if 'failed' in res:
                        if res['failed'] == 1:
                            ts = res['ts']
                        else:
                            response = self.get_long_poll_server(self.group_id)
                            if response is None:
                                return
                            ts = response['response']['ts']
                    else:
                        ts = res['ts']
                        for update in res['updates']:
                            # print('update', update)
                            if update['type'] == 'message_new':
                                self.parse_message(update["object"]["message"])
                except Exception as e:
                    print(f'Ошибка в while: {str(e)} res={res}')
                    answer = False
        except Exception as e:
            print(f'Ошибка: {str(e)} response={response}')

    def parse_message(self, message):  # Разбор входящих сообщений
        vk_search = self.reg_profile(message["from_id"])
        if vk_search is not None:
            if 'payload' in message:  # Нажата кнопка
                command = json.loads(message["payload"])['command']
                if command == 'next':
                    res = vk_search.next(1)
                    # print(res)
                    self.send_message(message["from_id"], f'Первая жертва: {res["last_name"]} {res["first_name"]} {res["id"]} количество фото {res["photos"]}')

                elif command == 'to_favorite':
                    self.send_message(message["from_id"], 'Действие: Добавили в избранное')
                    # print('to_favorite')

                elif command == 'favorites':
                    self.send_message(message["from_id"], 'Действие: Вывели список избранных')
                    # print('favorites')

                else:
                    self.send_message(message["from_id"], 'Действие: Что-то не понятное')
                    # print('else')


    #     if command['command'] == 'start':
    #         print(self.send_message(
    #             update["object"]["message"]["from_id"],
    #             update["object"]["message"]["peer_id"],
    #             'Проверка работы кнопки',
    #             None,
    #             [
    #                 # [['Регистрация', 'https://oauth.vk.com/authorize?client_id=51504958&scope=65536&response_type=token&redirect_uri=https://google.ru', 'positive']]
    #             ],
    #             True
    #         ))
    #         # print(self.send_message(
    #         #     update["object"]["message"]["from_id"],
    #         #     update["object"]["message"]["peer_id"],
    #         #     'Проверка работы кнопки',
    #         #     None,
    #         #     [
    #         #         [['Поиск', '{"command":"next"}', 'positive']],
    #         #         [['Избранные', '{"command":"favorites"}']]
    #         #     ]
    #         # ))
    #     else:
    #         print(self.send_message(
    #             update["object"]["message"]["from_id"],
    #             update["object"]["message"]["peer_id"],
    #             'Анкета',
    #             f'photo11994314_457239065_{self.params["access_token"]},photo11994314_305965580_{self.params["access_token"]}',
    #             []
    #         ))
