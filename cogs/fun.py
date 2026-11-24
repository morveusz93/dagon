import asyncio
import io
import logging
from typing import Awaitable, Callable

import aiohttp
import discord
from discord.ext import commands

import style
from errors import DagonError

log = logging.getLogger(__name__)

MOTIVATE_API_URL = "https://inspirobot.me/api?generate=true"
CATS_API_URL = "https://api.thecatapi.com/v1/images/search?limit=1"
DOGS_API_URL = "https://api.thedogapi.com/v1/images/search?limit=1"
DUCK_API_URL = "https://random-d.uk/api/v2/random"
FOX_API_URL = "https://randomfox.ca/floof/"

API_ERROR = "Dagonowi zabrakło dziś natchnienia. Spróbuj za chwilę."
FETCH_ERRORS = (
    aiohttp.ClientError,
    asyncio.TimeoutError,
    KeyError,
    IndexError,
    TypeError,
    ValueError,
)


class Fun(commands.Cog, description="🖼️ Malowidła"):
    def __init__(self, bot):
        self.bot = bot

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.http_session

    async def _json_field(self, url: str, *path):
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
        for key in path:
            data = data[key]
        return data

    async def _motivation_url(self) -> str:
        async with self.session.get(MOTIVATE_API_URL) as resp:
            resp.raise_for_status()
            return (await resp.text()).strip()

    async def _paint(
        self,
        ctx: commands.Context,
        title: str,
        get_url: Callable[[], Awaitable[str]],
    ):
        async with ctx.typing():
            try:
                img_url = await get_url()
                async with self.session.get(img_url) as resp:
                    resp.raise_for_status()
                    img = await resp.read()
            except FETCH_ERRORS as e:
                log.warning("Fetching picture for %s failed: %r", ctx.command, e)
                raise DagonError(API_ERROR) from e

            filename = "dagon" + _extension(img_url)
            embed = style.embed(
                f"Dagon namalował to dla {ctx.author.mention}.", title=title
            )
            embed.set_image(url=f"attachment://{filename}")
            await ctx.send(embed=embed, file=discord.File(io.BytesIO(img), filename))

    @commands.hybrid_command(
        description="Któż motywuje lepiej od Dagona?", aliases=["mot", "m"]
    )
    async def motivate(self, ctx):
        await self._paint(ctx, "✨ Motywacja", self._motivation_url)

    @commands.hybrid_command(description="Dagon jak wszyscy uwielbia kotki.")
    async def cat(self, ctx):
        await self._paint(
            ctx, "🐈 Kotek", lambda: self._json_field(CATS_API_URL, 0, "url")
        )

    @commands.hybrid_command(description="Dagon uwielbia również pieski.")
    async def dog(self, ctx):
        await self._paint(
            ctx, "🐕 Piesek", lambda: self._json_field(DOGS_API_URL, 0, "url")
        )

    @commands.hybrid_command(description="Dagon uwielbia malować kaczuszki.")
    async def duck(self, ctx):
        await self._paint(
            ctx, "🦆 Kaczuszka", lambda: self._json_field(DUCK_API_URL, "url")
        )

    @commands.hybrid_command(description="Dagon z przyjemnością namaluje Ci liska!")
    async def fox(self, ctx):
        await self._paint(
            ctx, "🦊 Lisek", lambda: self._json_field(FOX_API_URL, "image")
        )


def _extension(url: str) -> str:
    path = url.split("?", 1)[0].lower()
    for ext in (".gif", ".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return ".png"


async def setup(bot):
    await bot.add_cog(Fun(bot))
