from os import mkdir
from os.path import exists

from .__config__ import CONFIGURATION, VERSION, NAME, BUILD

from . import user
from . import store
from . import utils


if not exists(CONFIGURATION.CACHEPATH):
    mkdir(CONFIGURATION.CACHEPATH)


def __help__():
    print(f"LyPayAPI {VERSION}{':' + NAME if len(NAME) > 0 else ''} (build {BUILD})")
