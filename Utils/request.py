async def get_key_dict(session):
    async with session.get('https://api.prices.tf/items/5021;6?src=bptf') as response:
        return await response.json()
