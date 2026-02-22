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
        self.error_code = json["error"] if json is not None else None
        self.message = json["message"] if json is not None else None

    def __str__(self):
        return self.form_str_message()

    def form_str_message(self, custom_message: str | None = None) -> str:
        return f"""\
Получен код HTTP{self.status_code} при вызове {self.method}. \
Сообщение ядра: {self.error_code} {
        f"({custom_message})" if custom_message is not None else
        (f"({self.message})" if self.message is not None else "")
}
"""

    @classmethod
    def get(cls, method, response: ClientResponse, json: dict | None = None) -> APIError:
        """
        Автоматический определитель конкретной ошибки

        :param method: метод/функция библиотеки
        :param response: ответ от API
        :param json: ответ от API в формате JSON
        :return: экземпляр APIError
        """

        if json is None or 'message' not in json.keys():
            pass

        elif json['message'] == 'bad parsing':
            return BadRequest(method, response, json)

        elif json['message'] == 'invalid route':
            return InvalidRoute(method, response, json)

        elif json['message'] == 'email not found':
            return EmailNotFound(method, response, json)

        elif json['message'] == 'ID not found':
            return IDNotFound(method, response, json)
        elif json['message'] == 'ID already exists':
            return IDAlreadyExists(method, response, json)

        elif json['message'] == 'not enough balance':
            return NotEnoughBalance(method, response, json)
        elif json['message'] == 'subzero input':
            return SubZeroInput(method, response, json)

        elif json['message'] == 'avatar not found':
            return MediaNotFound(method, response, json)

        elif json['message'] == 'bad censor flag: user name':
            return InvalidUserName(method, response, json)
        elif json['message'] == 'bad censor flag: login':
            return InvalidUserLogin(method, response, json)

        elif json['message'] == 'bad censor flag: store name':
            return InvalidStoreName(method, response, json)
        elif json['message'] == 'bad censor flag: desc':
            return InvalidStoreDescription(method, response, json)

        return cls(method, response, json)


class IDNotFound(APIError):
    def __str__(self):
        return super().form_str_message("ID не был найден")


class EmailNotFound(APIError):
    def __str__(self):
        return super().form_str_message("эл. почта не была найдена в базе")


class IDAlreadyExists(APIError):
    def __str__(self):
        return super().form_str_message("ID уже существует")


class BadRequest(APIError):
    def __str__(self):
        return super().form_str_message("ядро не смогло обработать запрос")


class InvalidRoute(APIError):
    def __str__(self):
        return super().form_str_message("выбраный параметр пути некорректен")


class NotEnoughBalance(APIError):
    def __str__(self):
        return super().form_str_message("баланса пользователя недостаточно для оплаты")


class SubZeroInput(APIError):
    def __str__(self):
        return super().form_str_message("в поле для перевода введено число меньше нуля")


class MediaNotFound(APIError):
    def __str__(self):
        return super().form_str_message("медиа-контент не был найден")


class InvalidUserName(APIError):
    def __str__(self):
        return super().form_str_message("имя пользователя не прошло проверку")


class InvalidUserLogin(APIError):
    def __str__(self):
        return super().form_str_message("логин пользователя не прошёл проверку")


class InvalidStoreName(APIError):
    def __str__(self):
        return super().form_str_message("название магазина не прошло проверку")


class InvalidStoreDescription(APIError):
    def __str__(self):
        return super().form_str_message("описание магазина не прошло проверку")
