from aiohttp import ClientSession, TCPConnector
from ssl import create_default_context as ssl_create_default_context, CERT_NONE

from ..__config__ import CONFIGURATION
from ..__exceptions__ import APIError

host = CONFIGURATION.HOST
port = CONFIGURATION.PORT
cache_path = CONFIGURATION.CACHEPATH

ssl_context = ssl_create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = CERT_NONE


async def view(ID: int) -> int:
    """
    Запрос баланса пользователя

    :param ID: ID пользователя
    :return: число
    """

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/balance?ID={ID}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(view, response, json)

            return json["balance"]


async def deposit(ID: int, value: int, agent_id: int | None = None) -> None:
    """
    Функция пополнения баланса. Создаёт новую валюту в системе.

    Формально разрешено "отрицательное" зачисление, поэтому этой функции следует избегать при работе с любыми
    переводами во избежание излишних проверок; для переводов есть `transfer()`

    :param ID: ID пользователя
    :param value: сумма для зачисления
    :param agent_id: ID агента (необязательный аргумент, но необходимо указывать везде, где это возможно)
    :return: ничего (может вызвать ошибку выполнения)
    """

    agent_id_str = f"&agent_id={agent_id}" if agent_id is not None else ''
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/deposit?ID={ID}&value={value}" + agent_id_str) as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(deposit, response, json)


async def transfer(ID_out: int, ID_in: int | str, amount: int) -> None:
    """
    Функция перевода от покупателя покупателю (или магазину). Не изменяет количество валюты в системе.

    Ряд очевидных проверок проводится в самом ядре: сумма перевода положительна, оба ID существуют, у отправителя
    достаточно средств.

    Клиенту рекомендуется отдельно проверить случай ID_in = ID_out, к ошибке в ядре он не приведёт, но в общем случае
    пользователю сначала будет отправлено сообщение о снятии с его счёта денег, а потом сразу же о зачислении, что
    не является хорошим UX

    :param ID_out: ID пользователя (только покупатель)
    :param ID_in: ID получателя (другой покупатель или магазин)
    :param amount: сумма для перевода
    :return: ничего (может вызвать ошибку выполнения)
    """

    if type(ID_in) is int:
        mode = "t"  # transfer
    else:
        mode = "b"  # buy

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        async with session.get(f"{host}:{port}/user/transfer?ID_out={ID_out}&ID_in={ID_in}&amount={amount}&mode={mode}") as response:
            json = await response.json()
            if response.status >= 400:
                raise APIError.get(transfer, response, json)
