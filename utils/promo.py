from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError, IDNotFound, IDAlreadyExists

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def get_all() -> list[dict[str, ...]]:
    """
    Список всех сохранённых промокодов (словарей), активных и нет.
    Формат каждого словаря:

    | {
    | "ID": str,
    | "value": int,
    | "author": str,
    | "active": bool
    | }

    :return: список словарей с данными таблицы ``database.PROMO``
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/promo/all") as response:
            json = await response.json()
            if response.status >= 400:
                raise IDNotFound(get_all, response, json)

            return json['all']


async def get(ID: str) -> dict:
    """
    Запрос информации по конкретному промокоду.
    Формат данных:

    | {
    | "ID": str,
    | "value": int,
    | "author": str,
    | "active": bool
    | }

    :param ID: ID промокода
    :return: словарь с данными из таблицы ``database.PROMO``
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/promo/get",
                params={"ID": ID}
        ) as response:
            json = await response.json()
            if response.status >= 400:
                raise IDNotFound(get, response, json)

            return json


async def add(ID: str, value: int, author: str) -> None:
    """
    Добавляет новый промокод по переданным параметрам

    :param ID: ID промокода
    :param value: количество тугриков
    :param author: от кого выдан промокод (в родительном падаже, например "партии «Альянс»")
    :return: ничего (может вызвать ошибку выполнения)
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/promo/add",
                params={
                    "ID": ID,
                    "value": value,
                    "author": author
                }
        ) as response:
            json = await response.json()
            if response.status >= 400:
                if json["message"] == "ID already exists":
                    raise IDAlreadyExists(edit, response, json)
                raise APIError(add, response, json)


async def edit(ID: str, value: int | None = None, author: str | None = None, active: bool | None = None) -> None:
    """
    Изменяет любой указанный параметр промокода по введённому ID. Обязателен хотя бы один аргумент кроме ID.

    :param ID: ID промокода
    :param value: количество тугриков
    :param author: от кого выдан промокод (в родительном падаже, например "партии «Альянс»")
    :param active: флаг, отвечающий за возможность ввести промокод
    :return: ничего (может вызвать ошибку выполнения)
    """

    payload = dict()
    if value is not None:
        payload["value"] = value
    if author is not None:
        payload["author"] = author
    if active is not None:
        payload["active"] = active
    if len(payload) == 0:
        raise ValueError("В вызове функции promo.edit должен присутствовать хотя бы один аргумент кроме ID.")
    payload["ID"] = ID

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(
                f"{host}:{port}/promo/edit",
                params=payload
        ) as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError(edit, response, json)
