import logging

import aiohttp
import discord
from discord.ext import commands

from config import COC, COMMAND_PREFIX

# Kolejność = kolejność sekcji w /help
EXTENSIONS = (
    "cogs.rpg",
    "cogs.fun",
    "cogs.mayo",
    "cogs.postac",  # loads only when COC_* is configured
    "cogs.core",
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
            help_command=None,
        )
        self.text_prefix = COMMAND_PREFIX
        self.http_session: aiohttp.ClientSession | None = None

    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        for ext in EXTENSIONS:
            await self.load_extension(ext)
        synced = await self.tree.sync()
        log.info("Synced %d slash commands", len(synced))
        if COC is not None:
            # /postac lives on the party's server only, so it needs its own guild sync.
            guild = discord.Object(id=COC.guild_id)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d slash commands for guild %s", len(synced), COC.guild_id)
        else:
            log.info(
                "/postac is off (COC_APP_URL, COC_LINK_SECRET or COC_GUILD_ID missing)"
            )

    async def close(self):
        if self.http_session:
            await self.http_session.close()
        await super().close()

    async def on_ready(self):
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
