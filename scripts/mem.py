from aiohttp import ClientResponse
from aiofiles import open as a_open

async def save_iterative(response: ClientResponse, path: str, chunk: int):
    """
    Сохраняет контент response по пути path по чанкам (см. CONFIGURATION)

    :param response: переменная ответа сервера
    :param path: путь для сохранения
    :param chunk: размер чанка скачивания
    """

    async with a_open(path, mode='wb') as f:
        async for chunk in response.content.iter_chunked(chunk):
            await f.write(chunk)
