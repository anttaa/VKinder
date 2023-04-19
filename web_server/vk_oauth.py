import json

from aiohttp import web, ClientSession
import sqlite3
import ssl

SCOPES = "offline,photos"
REDIRECT_URI = "https://178.57.222.71:8080/social_login/vk/callback"
REDIRECT_GROUP = "https://vk.com/im?sel=-219663170"
DIALOG_URI = f"https://oauth.vk.com/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPES},v=5.93"
TOKEN_URI = "https://oauth.vk.com/access_token?client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}"


async def handle(request):
    return web.HTTPFound(DIALOG_URI)


async def handler_callback(request):
    code = request.query.get("code")
    uri = TOKEN_URI.format(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        code=code,
    )
    async with ClientSession() as session:
        async with session.post(uri) as response:
            response_data = await response.json()
            conn = sqlite3.connect("/root/vk_bot/database")
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=wal")
            cursor.execute(
                "update profiles set token=? where vk_id=?",
                (response_data["access_token"], response_data["user_id"]),
            )
            conn.commit()
            cursor.close()
            conn.close()

    return web.HTTPFound(REDIRECT_GROUP)  # web.json_response(response_data)


app = web.Application()
app.add_routes(
    [web.get("/", handle), web.get("/social_login/vk/callback", handler_callback)]
)

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("certificate.crt", "private.key")
web.run_app(app, ssl_context=ssl_context, port=8080)
