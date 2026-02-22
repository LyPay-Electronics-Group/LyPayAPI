from ..__config__ import CONFIGURATION


def censor(field: str) -> bool:
    """
    Проверяет, есть ли в строке символы, которые потенциально могут вызвать непредвиденное поведение ядра:
    '<', '>', '&' (не в составе специальных последовательностей "&amp;", "&lt;", "&gt;"

    :param field: поле для строки
    :return: True, если строка прошла проверку, False -- в обратном случае
    """

    for index in range(len(field)):
        char = field[index]
        if char == '<' or char == '>':
            return False
        if char == '&' and field[index:index+3] not in ('&lt;', '&gt;') and field[index:index+4] != '&amp;':
            return False
    return True


def check_name(name: str) -> bool:
    """
    Проверяет введённое пользователем имя. Имя может состоять из следующих символов:
    ``А-Я``, ``а-я``, ``-``, ``–``, ``[пробел]`` (актуальный список прописан в конфигурационном файле)

    :param name: имя
    :return: True, если имя прошло проверку, False -- в обратном случае
    """

    for char in name:
        if char not in CONFIGURATION.CORRECT_NAME_LITERALS:
            return False
    return True


def check_login(login: str) -> bool:
    """
    Проверяет введённый пользователем логин. Логин может состоять из следующих символов:
    ``A-Z``, ``a-z``, ``-``, ``.``, ``_`` (актуальный список прописан в конфигурационном файле)

    :param login: логин
    :return: True, если логин прошёл проверку, False -- в обратном случае
    """

    for char in login:
        if char not in CONFIGURATION.CORRECT_LOGIN_LITERALS:
            return False
    return True
