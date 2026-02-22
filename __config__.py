from os import getcwd


class CONFIGURATION:
    CACHEPATH = getcwd() + '/lypay_api_cache/'

    CHUNK_SIZE = 512

    HOST = "http://localhost"
    PORT = 8128

VERSION = "test-1"
NAME = ""
BUILD = 6
