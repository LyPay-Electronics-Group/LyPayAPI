from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from aiofiles import open as a_open
from os.path import getmtime, exists
from os import remove

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def get(ID: int) -> dict[str, ...]:
    """
    Запрос данных о пользователе в следующем формате:

    | {
    | "ID": int,
    | "name": str,
    | "login": str | None,
    | "password": str | None,
    | "class": str,
    | "email": str,
    | "tag": str | None,
    | "balance": int,
    | "owner": int
    | }

    :param ID: ID пользователя
    :return: словарь с данными пользователя из таблицы ``database.USERS``
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/get?ID={ID}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(get, response, json)

            return json


async def get_all() -> list[int]:
    """
    Запрос всех существующих ID пользователей

    :return: список с ID из таблицы ``database.USERS``
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/get_all") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(get_all, response, json)

            return json['ids']


async def _request_qr(ID: int, path: str) -> None:
    """
    Внутренняя функция, не рекомендуется использовать без обёртки `qr()`
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/qr/get?ID={ID}") as response:
            if response.status >= 400:
                raise APIError.get(_request_qr, response, await response.json())

            async with a_open(path, mode='wb') as f:
                async for chunk in response.content.iter_chunked(CONFIGURATION.CHUNK_SIZE):
                    await f.write(chunk)


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
                if response.status >= 400:
                    raise APIError.get(qr, response, json)

                if not json["actual"]:
                    remove(path)
                if not json["exists"] or not json["actual"]:
                    await _request_qr(ID, path)
                return path


    else:
        await _request_qr(ID, path)
        return path
