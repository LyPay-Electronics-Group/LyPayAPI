from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from ...__config__ import CONFIGURATION
from ...__exceptions__ import APIError

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def get(ID: str) -> str:
    """
    Запрос данных об описании магазина

    :param ID: ID магазина
    :return: описание
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/store/settings/desc/get",
                params={"ID": ID}
        ) as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(get, response, json)

            return json['result']


async def update(ID: str, new: str):
    """
    Обновление описания магазина

    :param ID: ID магазина
    :param new: новое описание
    :return: ничего (может вызвать ошибку выполнения)
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/store/settings/desc/set",
                params={
                    "ID": ID,
                    "new": new
                }
        ) as response:
            if response.status >= 400:
                raise APIError.get(update, response, await response.json())
