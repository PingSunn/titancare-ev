from prisma import Prisma

_client: Prisma | None = None


async def get_client() -> Prisma:
    global _client
    if _client is None or not _client.is_connected():
        _client = Prisma()
        await _client.connect()
    return _client


async def disconnect():
    global _client
    if _client and _client.is_connected():
        await _client.disconnect()
        _client = None
