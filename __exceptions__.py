from aiohttp import ClientResponse


class APIError(Exception):
    def __init__(self, method, response: ClientResponse, json: dict | None = None):
        """
        Класс ошибки API

        :param method: метод/функция библиотеки
        :param response: ответ от API
        """
        self.method = method.__module__ + '.' + method.__name__
        self.status_code = response.status
        self.error_code = json["error"] if json else None

    def __str__(self):
        return f"""
Получен код HTTP{self.status_code} при вызове {self.method}. \
Сообщение ядра: {self.error_code}.
"""


class UserNotFound(APIError):
    def __str__(self):
        return f"""
Получен код HTTP{self.status_code} при вызове {self.method}. \
Сообщение ядра: {self.error_code} (пользователь не был найден).
"""
