import requests
import random
import json

from handler.keyboard import make_keyboard
from vk_search import VkSearch
from handler.tools import profile_check
from vk_profile import VkUser


class UserHandler:
    url = "https://api.vk.com/method"

    def __init__(
        self,
        db_session,
        group_id: int,
        version: str,
        token_group: str,
        token_search: str,
    ):
        self.__db_session = db_session
        self.__session = {}
        self.__group_id = group_id
        self.__params_search = {"access_token": token_search}
        self.__params = {"access_token": token_group, "v": version}
        self.__reg_long_poll_server()

    def __get_long_poll_server(self, group_id):  # Запрос сервера
        try:
            params = {"group_id": group_id}
            return requests.get(
                f"{self.url}/groups.getLongPollServer",
                params={**self.__params, **params},
            ).json()
        except Exception as e:
            return None

    def __reg_long_poll_server(self):  # Запускаем сервер
        serv_param = None
        try:
            serv_param = self.__get_long_poll_server(self.__group_id)
            if serv_param is None:
                return
            serv_param = serv_param["response"]
            ts = serv_param["ts"]
            answer = True
            res = None
            while answer:
                try:
                    res = requests.get(
                        f'{serv_param["server"]}?act=a_check&key={serv_param["key"]}&ts={ts}&wait=25'
                    ).json()
                    if "failed" in res:
                        if res["failed"] == 1:
                            ts = res["ts"]
                        else:
                            serv_param = self.__get_long_poll_server(self.__group_id)
                            if serv_param is None:
                                return
                            ts = serv_param["response"]["ts"]
                    else:
                        ts = res["ts"]
                        for update in res["updates"]:
                            if update["type"] == "message_new":
                                self.__parse_message(update["object"]["message"])
                except Exception as e:
                    print(f"Ошибка в while: {str(e)} res={res}")
                    answer = False
        except Exception as e:
            print(f"Ошибка: {str(e)} serv_param={serv_param}")

    def __send_message(
        self,
        user_id: int,
        message: dict  # {'text': '', 'attachment': '', 'btn_in_mes': True\False, 'buttons':[]}
        # message: str,
        # attachment: str = None,
        # buttons: list = None,
        # btn_in_mes: bool = False,
    ):
        # https://dev.vk.com/method/messages.send
        try:
            params = {
                "user_id": user_id,
                "peer_id": user_id,
                "random_id": random.randint(1, 10000),
            }

            if "text" in message:
                params["message"] = message["text"]

            if "attachment" in message:
                params["attachment"] = message["attachment"]

            if "btn_in_mes" not in message:
                message["btn_in_mes"] = False

            if "buttons" in message:
                params["keyboard"] = make_keyboard(
                    [message["buttons"]], message["btn_in_mes"]
                )
            return requests.get(
                f"{self.url}/messages.send", params={**self.__params, **params}
            ).json()
        except Exception as e:
            print(f"__send_message_error: {str(e)}")

    def __parse_message(self, message):  # Разбор входящих сообщений
        try:
            if message["from_id"] not in self.__session:
                self.__session[message["from_id"]] = {"profile": None, "handler": None}
            session = self.__session[message["from_id"]]
            if session["profile"] is None:  # Загружаем профиль
                session["profile"] = VkUser(
                    self.__db_session, message["from_id"], self.__params["access_token"]
                )
                session["profile"].save()
                session["client"] = None
                session["favorite_offset"] = 0
                # self.__load_profile(message["from_id"])
            answer = False
            check = profile_check(session["profile"])
            cmd = self.default_cmd
            command = "default_cmd"
            if "payload" in message:  # Нажата кнопка
                command = json.loads(message["payload"])["command"]
            if (
                len(check) > 0
                and session["handler"] is None
                and command.find("setting") == -1
            ):
                answer = self.__menu_settings()
                answer["text"] = f"{check} {answer['text']}"
            else:
                if session["handler"] is not None and command.find("cancel") == -1:
                    cmd = session["handler"]
                elif command in dir(self):
                    cmd = getattr(self, command)
                try:
                    answer = cmd(session, message["text"])
                except Exception as e:
                    print("cmd:", e)
            if type(answer) is list:
                for mes in answer:
                    self.__send_message(message["from_id"], mes)
            else:
                if answer:
                    self.__send_message(message["from_id"], answer)
        except Exception as e:
            print("parse_message", e)

    def __menu_main(self):
        return {
            "text": "Главное меню",
            "buttons": [
                [
                    ["В избранное", '{"command":"to_favorite"}', "primary"],
                    ["Следующий", '{"command":"next"}', "primary"],
                ],
                [["Избранные", '{"command":"favorites"}', "primary"]],
                [["Настройки", '{"command":"settings"}', "primary"]],
            ],
        }

    def __menu_settings(self):
        return {
            "text": '<br>Меню "Настройки"',
            "buttons": [
                [
                    ["Возраст", '{"command":"setting_age"}', "primary"],
                    ["Город", '{"command":"setting_city"}', "primary"],
                    ["Пол", '{"command":"setting_sex"}', "primary"],
                ],
                [["Обновить из профиля", '{"command":"setting_update"}', "primary"]],
                [["Регистрация", "https://178.57.222.71:8080/", None, "open_link"]],
                [["<- Назад", '{"command":"default_cmd"}', "primary"]],
            ],
        }

    def __menu_favorites(self):
        return {
            "text": "Избранные",
            "buttons": [
                [
                    [
                        "Предыдущая страница",
                        '{"command":"favorites_prev_page"}',
                        "primary",
                    ],
                    [
                        "Следующая страница",
                        '{"command":"favorites_next_page"}',
                        "primary",
                    ],
                ],
                [["<- Назад", '{"command":"default_cmd"}', "primary"]],
            ],
        }

    def default_cmd(self, session, text):
        session["handler"] = None
        return self.__menu_main()

    def settings(self, session, text):
        session["handler"] = None
        return self.__menu_settings()

    def setting_cancel(self, session, text):
        session["handler"] = None
        return self.__menu_main()

    def setting_get_token(self, session, text):
        session["handler"] = None
        return {
            "text": "Укажите возраст:"
            if session["profile"].age != -1
            else f"Ваш возраст {session['profile'].age}. Укажите новый:",
            "buttons": [[["Отмена", '{"command":"settings_cancel"}', "primary"]]],
        }

    def setting_age(self, session, text):
        session["handler"] = self.setting_age_save
        return {
            "text": "Укажите возраст:"
            if session["profile"].age != -1
            else f"Ваш возраст {session['profile'].age}. Укажите новый:",
            "buttons": [[["Отмена", '{"command":"settings_cancel"}', "primary"]]],
        }

    def setting_age_save(self, session, text):
        session["handler"] = None
        session["profile"].age = int(text)
        session["profile"].save()
        mes = self.__menu_settings()
        mes["text"] = f"Возраст сохранен {mes['text']}"
        return mes

    def setting_city(self, session, text):
        session["handler"] = self.setting_city_save
        return {
            "text": "Укажите город:"
            if session["profile"].age != -1
            else f"Ваш город {session['profile'].age}. Укажите новый:",
            "buttons": [[["Отмена", '{"command":"settings_cancel"}', "primary"]]],
        }

    def setting_city_save(self, session, text):
        session["handler"] = None
        session["profile"].city = int(text)
        session["profile"].save()
        mes = self.__menu_settings()
        mes["text"] = f"Город сохранен {mes['text']}"
        return mes

    def setting_sex(self, session, text):
        session["handler"] = self.setting_sex
        return {
            "text": "Укажите пол:",
            "buttons": [
                [
                    ["Мужской", '{"command":"setting_sex_save_male"}', "primary"],
                    ["Женский", '{"command":"setting_sex_save_female"}', "primary"],
                ],
                [["Отмена", '{"command":"settings_cancel"}', "primary"]],
            ],
        }

    def setting_sex_save_male(self, session, text):
        # self.__session[peer_id]["handler"] = None
        session["handler"] = self.setting_sex
        session["profile"].sex = 1
        # return {"text": "Действие: Добавили в избранное"}
        return self.__menu_settings()

    def setting_sex_save_female(self, session, text):
        # self.__session[peer_id]["handler"] = None
        session["handler"] = self.setting_sex
        session["profile"].sex = 2
        # return {"text": "Действие: Добавили в избранное"}
        return self.__menu_settings()

    def setting_update(self, session, text):
        session["handler"] = None
        # return {"text": "Действие: Добавили в избранное"}
        return self.__menu_settings()

    def next(self, session, text):
        try:
            if session["client"] is not None:
                self.__db_session.candidates_save(session["profile"], session["client"])

            session["client"] = VkSearch(session["profile"], self.__db_session).next()
            return {
                "text": f'{session["client"].last_name} {session["client"].first_name}\n https://vk.com/id{session["client"].vk_id}',
                "attachment": session["client"].photos,
            }
        except Exception as e:
            print("next", e)

    def to_favorite(self, session, text):
        if session["client"] is not None:
            self.__db_session.candidates_save(session["profile"], session["client"], 1)
        session["client"] = None
        return self.next(session, text)

    def favorites(self, session, text):
        session["handler"] = None
        session["favorite_offset"] = 0
        # self.favorites_next_page(session, text)
        return self.__menu_favorites()

    def favorites_prev_page(self, session, text):
        data = []
        if session["favorite_offset"] - 10 < 0:
            session["favorite_offset"] = 0
        res = self.__db_session.favorite_load(
            session["profile"], session["favorite_offset"]
        )
        # self.__menu_favorites()
        for rec in res:
            data.append(
                {
                    "text": f'{rec["last_name"]} {rec["first_name"]}\n https://vk.com/id{rec["vk_id"]}',
                    "attachment": rec["photos"],
                }
            )
        return data

    def favorites_next_page(self, session, text):
        data = []
        res = self.__db_session.favorite_load(
            session["profile"], session["favorite_offset"]
        )
        for rec in res:
            data.append(
                {
                    "text": f'{rec["last_name"]} {rec["first_name"]}\n https://vk.com/id{rec["vk_id"]}',
                    "attachment": rec["photos"],
                }
            )
        # self.__menu_favorites()
        session["favorite_offset"] += 10
        return data
