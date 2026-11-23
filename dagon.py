import logging

import aiohttp
import discord
from discord.ext import commands

from config import COMMAND_PREFIX

EXTENSIONS = (
    "cogs.fun",
    "cogs.rpg",
)

log = logging.getLogger(__name__)


class Dagon(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = False

        super().__init__(
            command_prefix=commands.when_mentioned_or(COMMAND_PREFIX),
            intents=intents,
        )
        self.http_session: aiohttp.ClientSession | None = None

    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        for ext in EXTENSIONS:
            await self.load_extension(ext)

    async def close(self):
        if self.http_session:
            await self.http_session.close()
        await super().close()

    async def on_ready(self):
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
