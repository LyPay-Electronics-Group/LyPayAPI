from os import getcwd


class CONFIGURATION:
    CACHEPATH = getcwd() + '/lypay_api_cache/'

    CHUNK_SIZE = 512

    HOST = "http://localhost"
    PORT = 8128

    CORRECT_NAME_LITERALS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя -–АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    CORRECT_LOGIN_LITERALS = set("abcdefghijklmnopqrstuvwxyz._-ABCDEFGHIJKLMNOPQRSTUVWXYZ")

VERSION = "test-1"
NAME = ""
BUILD = 6
