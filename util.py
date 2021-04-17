import aiohttp


async def get_new_emotes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
