from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from ..scripts import j2
from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def check_email_record(email: str) -> dict[str, ...]:
    """
    Запрос данных в таком формате:

    | {
    | "name": str,
    | "email": str,
    | "group": str
    | }

    :param email: эл. почта пользователя
    :return: словарь с данными пользователя из таблицы ``database.CORPORATION``
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/reg/email/corp_record?email={email}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(check_email_record, response, json)

            return json


async def send_email(route: str, participant: str, code: str | int, keys: dict[str, ...] | None = None) -> None:
    """
    Отправляет письмо по эл. почте

    :param route: 'main' или 'guest' -- два разных шаблона письма для лицеистов/сотрудников и гостей Ярмарки
    :param participant: почта получателя
    :param code: код верификации пользователя
    :param keys: словарь ключей для замены в итоговом письме (выставляется по умолчанию)
    :return: ничего (может вызвать ошибку выполнения)
    """

    keys_str = f"&keys={j2.to_(keys, string_mode=True)}" if keys is not None else ''
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/reg/email/send?route={route}&email={participant}&code={code}{keys_str}") as response:
            if response.status >= 400:
                raise APIError.get(check_email_record, response, await response.json())


async def new(*, name: str, login: str | None, password: str | None, group: str, email: str, tag: str | None, owner_flag: str) -> int:
    """
    Регистрация нового пользоавтеля
    :param name: имя (по таблцие ``database.CORPORATION``)
    :param login: логин (тестовая сборка: пропущено)
    :param password: пароль (тестовая сборка: пропущено)
    :param group: группа (по таблице ``database.CORPORATION``)
    :param email: эл. почта
    :param tag: telegram tag
    :param owner_flag: 'tg_owner', 'tg_guest', 'web_owner', 'web_guest' или 'integration' (для каждой платформы клиент должен сам контролировать этот аргумент)
    :return: ID новой записи
    """

    args = f"name={name}&group={group}&email={email}&owner_flag={owner_flag}"
    if login is not None and password is not None:
        args += f"&login={login}&password={password}"
    if tag is not None:
        args += f"&tag={tag}"

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/reg/user?{args}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(check_email_record, response, json)

            return json['ID']
