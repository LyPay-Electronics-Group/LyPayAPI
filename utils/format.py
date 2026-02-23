keymap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    '\'': '&#x27;'
}


def clear(line: str) -> str:
    """
    Очищает строку от символов, которые не проходят проверку в ядре
    (``>``, ``<``, ``"``, ``'``, ``&``)

    :param line: строка
    :return: строка с экранированными последовательностями
    """

    for key, value in keymap.items():
        line = line.replace(key, value)
    return line


def rollback(line: str) -> str:
    """
    Возвращает очищенные символы обратно

    :param line: строка
    :return: строка с обратно преобразованными последовательностями
    """

    for key, value in reversed(keymap.items()):
        line = line.replace(key, value)
    return line
