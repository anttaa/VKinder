# Документация к командному проекту по курсу «Профессиональная работа с Python»

## VKinder

### Установка

1. Убедитесь, что компьютер настроен для работы с БД PostgreSQL. Ссылка для установки: [Postgre](https://www.postgresql.org/).
2. Для копирования файлов проекта Вам потребуется аккаунт на GitHub. Ссылка: [GiThub](https://github.com/).
3. Создайте группу в ВКонтакте, от имени которой будет общаться бот. Инструкцию можно посмотреть [здесь](group_settings.md).
4. Получите токен для группы ВКонтакте, выполнив [инструкцию](https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit?usp=sharing).
5. Склонируйте репозиторий с проектом на свой компьютер.
6. Сохраните токен группы в переменной vk_group в файле settings.ini.
7. Создайте приложение для чат-бота [ВКонтакте](https://dev.vk.com/).
8. Используя id и секретный ключ приложения, заполните соответствующие поля в файле vk_oauth.py (CLIENT_ID и CLIENT_SECRET).
9. Запустите сервер [Postgre](https://www.postgresql.org/docs/).
10. Создайте базу данных.
11. Подключите базу данных к СУБД, указав адрес сервера, название БД, логин и пароль пользователя.
12. Запустите файл main.py в любой IDE.


------


### Инструкция для взаимодействия с ботом

- Для начала взаимодействия с ботом, напишите сообщение в чат группы. Повторно нажмите на кнопку "Сообщения" и далее "Перейти к диалогу с сообществом".
- При первом взаимодействии с ботом потребуется подтвердить доступ приложения к своим персональным данным (ФИО, город, возраст).
- Если какие-либо данные пользователя не указаны в профиле, откроется меню "Настройки", где будет предложено ввести недостающие данные самостоятельно.
- Если все данные пользователя получены приложением, откроется главное меню.
- При нажатии кнопки "Следующий", бот предложит анкету пользователя, содержащую имя и фамилию кандидата, ссылку на профиль VK и три фотографии профиля кандидата с наибольшим количеством лайков.
- С помощью кнопки "В избранное", можно добавить кандидата в список избранных.
- Список избранных кандидатов выводится по нажатию на кнопку "Избранные".
- Навигация в меню "Избранные" осуществляется кнопками "Предыдущая страница"/"Следующая страница". 
- Можно удалить профиль кандидата из списка избранных, с помощью кнопки "Убрать из избранного".
- В меню "Настройки" можно удалить профиль пользователя с помощью одноименной кнопки.
