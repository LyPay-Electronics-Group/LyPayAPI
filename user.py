from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from aiofiles import open as a_open
from os.path import getmtime, exists
from os import remove

from .__config__ import CONFIGURATION
from .__exceptions__ import APIError, UserNotFound

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def info(ID: int) -> dict:
    """
    Запрос данных о пользователе

    :param ID: ID пользователя
    :return: словарь со строкой таблицы USERS
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/info?ID={ID}") as response:
            json = await response.json()
            if response.status // 100 == 2:
                return json

            raise UserNotFound(info, response, json)


async def balance(ID: int) -> int:
    """
    Запрос баланса пользователя

    :param ID: ID пользователя
    :return: число
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/balance?ID={ID}") as response:
            json = await response.json()
            if response.status // 100 == 2:
                return json["balance"]

            raise UserNotFound(balance, response, json)


async def _download_qr(ID: int, path: str) -> None:
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/qr/get?ID={ID}") as response:
            if response.status // 100 == 2:
                async with a_open(path, mode='wb') as f:
                    async for chunk in response.content.iter_chunked(CONFIGURATION.CHUNK_SIZE):
                        await f.write(chunk)
                return

            raise APIError(_download_qr, response, await response.json())


async def qr(ID: int) -> str:
    """
    Проверяет актуальность QR с ID пользователя, в случае необходимости запрашивает новые данные с сервера и сохраняет их локально

    :param ID: ID пользователя
    :return: абсолютный путь до файла (независимо от того, было обновление или нет)
    """

    path = cache_path + f"{ID}.png"

    if exists(path):
        async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
            async with session.get(f"{host}:{port}/user/qr/check?ID={ID}&unix={getmtime(path)}") as response:
                json = await response.json()
                if response.status // 100 == 2:
                    if not json["actual"]:
                        remove(path)
                    if not json["exists"] or not json["actual"]:
                        await _download_qr(ID, path)
                    return path

                raise APIError(qr, response, json)

    else:
        await _download_qr(ID, path)
        return path
