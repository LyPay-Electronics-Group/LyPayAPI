from aiohttp import ClientResponse
from aiofiles import open as a_open

from .__config__ import CONFIGURATION

async def save_iterative(response: ClientResponse, path: str):
    """
    Сохраняет контент response по пути path по чанкам (см. CONFIGURATION)

    :param response: переменная ответа сервера
    :param path: путь для сохранения
    """

    async with a_open(path, mode='wb') as f:
        async for chunk in response.content.iter_chunked(CONFIGURATION.CHUNK_SIZE):
            await f.write(chunk)
