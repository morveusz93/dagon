import asyncio
import os

from dagon import Dagon
from cogs.music import setup_music
from cogs.rpg import setup_rpg
from cogs.fun import setup_fun

TOKEN = os.getenv("DISCORD_TOKEN")


async def main():
    bot = Dagon()
    async with bot:
        await setup_music(bot)
        await setup_rpg(bot)
        await setup_fun(bot)
        await bot.start(TOKEN)


asyncio.run(main())
