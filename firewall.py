from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from .__config__ import CONFIGURATION
from .__exceptions__ import APIError

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
    if route not in ('main', 'stores', 'admins'):
        raise ValueError("Аргумент route указан неверно.")

    user = await entry(ID, route)
    if user is not None:
        return user['access']
    elif route == 'main':
        return True
    return False


async def entry(ID: int, route: str) -> dict | None:
    """
    Запрос профиля пользователя в файерволле

    :param ID: ID пользователя
    :param route: 'main', 'stores' или 'admins'
    :return: словарь с данными пользователя из таблицы firewall.STORES, если запись существует, иначе None
    """

    route = route.strip().lower()
    if route not in ('main', 'stores', 'admins'):
        raise ValueError("Аргумент route указан неверно.")

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/fw/{route}?ID={ID}") as response:
            json = await response.json()
            if response.status // 100 == 2:
                if json['found']:
                    return json['entry']
                return None
            raise APIError(entry, response, json)
