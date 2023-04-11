import configparser
from handler.user_handler import UserHandler
from base import Database

if __name__ == "__main__":
    ini = configparser.ConfigParser()
    ini.read("settings.ini")

    base = Database("database")
    uh = UserHandler(
        base,
        ini.getint("vk", "group_id"),
        ini.get("vk", "version"),
        ini.get("tokens", "vk_group"),
        ini.get("tokens", "vk_personal"),
    )
