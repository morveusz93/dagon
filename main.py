import asyncio
import os

from dagon import Dagon
from music import setup_music
from others import setup_others

TOKEN = os.getenv("DISCORD_TOKEN")


async def main():
    bot = Dagon()
    async with bot:
        await setup_music(bot)
        await setup_others(bot)
        await bot.start(TOKEN)


asyncio.run(main())
