import logging
import re

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

# Tylko "Winiary" i "WINIARY" - bez odmiany i bez małych liter
WINIARY = re.compile(r"\b(?:Winiary|WINIARY)\b")
REACTION = "🤮"


class Mayo(commands.Cog, description="🥚 Majonez"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not mentions_winiary(message.content):
            return
        try:
            await message.add_reaction(REACTION)
        except discord.HTTPException as e:  # np. brak uprawnienia Add Reactions
            log.warning("Could not react in #%s: %r", message.channel, e)


def mentions_winiary(text: str) -> bool:
    return WINIARY.search(text) is not None


async def setup(bot):
    await bot.add_cog(Mayo(bot))
