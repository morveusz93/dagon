import asyncio
import os

from dagon import Dagon
from music import setup_music

TOKEN = os.getenv("DISCORD_TOKEN")


async def main():
    bot = Dagon()
    async with bot:
        await setup_music(bot)
        await bot.start(TOKEN)


asyncio.run(main())
