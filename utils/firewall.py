from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError, IDNotFound

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def check(ID: int, route: str) -> bool:
    """
    Быстрая проверка доступа

    :param ID: ID пользователя
    :param route: 'main', 'stores' или 'admins'
    :return: True, если доступ разрешён, False -- в противном случае
    """

    route = route.strip().lower()
    try:
        user = await entry(ID, route)
        return user['access']
    except IDNotFound:
        if route == 'main':
            return True
        return False


async def entry(ID: int, route: str) -> dict:
    """
    Запрос профиля пользователя в файерволле в формате:

    | {
    | "ID": int,
    | "unix": float,
    | "access": bool,
    | "comment": str | None
    | }

    :param ID: ID пользователя
    :param route: 'main', 'stores' или 'admins'
    :return: словарь с данными пользователя из таблицы ``firewall.STORES``
    """

    route = route.strip().lower()
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/fw/{route}?ID={ID}") as response:
            json = await response.json()
            if response.status // 100 == 2:
                if json['found']:
                    return json['entry']
                raise IDNotFound(entry, response, json)
            raise APIError.get(entry, response, json)
