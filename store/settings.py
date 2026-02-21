from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from os.path import getmtime, exists
from os import remove

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError
from ..mem import save_iterative

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
    if exists(path):
        unix_str = f"&unix={getmtime(path)}"
    else:
        unix_str = ""

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/settings/avatar/get?ID={ID}{unix_str}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(get_avatar, response, json)

            if json['result'] == "no icon":
                if exists(path):
                    remove(path)
                return None
            if json['result'] == "avatar didn't change":
                return path

            await save_iterative(response, path, CONFIGURATION.CHUNK_SIZE)
            return path
