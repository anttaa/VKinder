from datetime import date, datetime


def calculate_age(bdate):
    bdate = datetime.strptime(bdate, "%d.%m.%Y")
    today = date.today()
    age = (
            today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    )
    return age


def profile_vk_check(vk_profile):
    if "bdate" in vk_profile:
        if len(vk_profile["bdate"].split(".")) < 3:
            vk_profile["age"] = -1
        else:
            vk_profile["age"] = calculate_age(vk_profile["bdate"])
        del vk_profile["bdate"]
    else:
        vk_profile["age"] = -1

    if "sex" in vk_profile:
        if vk_profile["sex"] == 0:
            vk_profile["sex"] = -1
    else:
        vk_profile["sex"] = -1

    if "city" in vk_profile:
        vk_profile["city"] = vk_profile["city"]["id"]
    else:
        vk_profile["city"] = -1

    return vk_profile


def profile_check(profile):
    err = ""
    try:
        if profile.token == -1:
            err += (
                " - Для использования поиска необходимо зарегистрироваться<br>"
            )

        if profile.age == -1:
            err += (
                " - Не удается определить Ваш возраст, так как скрыта дата рождения<br>"
            )

        if profile.sex == -1:
            err += " - Не удается определить Ваш пол<br>"

        if profile.city == -1:
            err += " - У Вас не указан город<br>"

        return (
            f"Есть ошибки: <br> {err} <br>Необходимо указать недостающие данные"
            if len(err) > 0
            else ""
        )
    except Exception as e:
        print("check_profile", e)
        return err
