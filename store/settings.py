from aiohttp import ClientSession, TCPConnector, FormData
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from os.path import getmtime, exists
from os import remove
from aiofiles import open as a_open

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError
from ..scripts.mem import save_iterative

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def get_avatar(ID: str) -> str | None:
    """
    Запрос данных об аватаре магазина

    :param ID: ID магазина
    :return: None, если аватара нет (или больше нет), в противном случае -- путь до файла с кэшем аватара.
    """

    path = CONFIGURATION.CACHEPATH + f"stores_media_{ID}.jpg"
    payload = dict()
    payload["ID"] = ID
    if exists(path):
        payload["unix"] = getmtime(path)

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/store/settings/avatar/get",
                params=payload
        ) as response:
            if "json" in response.content_type:
                json = await response.json()
            else:
                json = {"message": "unknown", "error": "unknown", "result": "got image content"}

            if response.status >= 400:
                raise APIError.get(get_avatar, response, json)

            if json['result'] == "no icon":
                if exists(path):
                    remove(path)
                return None

            if json['result'] != "avatar didn't change":
                await save_iterative(response, path, CONFIGURATION.CHUNK_SIZE)
            return path


async def set_avatar(ID: str, media_path: str):
    """
    Запрос данных об аватаре магазина

    :param ID: ID магазина
    :param media_path: путь (абсолютный) до файла с аватаром
    :return: ничего (может вызвать ошибку выполнения)
    """

    media_type = media_path.split(".")[-1]
    form = FormData()
    async with a_open(media_path, 'rb') as avatar:
        form.add_field(
            "avatar",
            await avatar.read(),
            content_type=f"image/{media_type}"
        )

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.post(
                f"{host}:{port}/store/settings/avatar/set",
                params={"ID": ID},
                data=form
        ) as response:
            if response.status >= 400:
                raise APIError.get(get_avatar, response, await response.json())
