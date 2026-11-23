import io
import logging

import aiohttp
import discord
from discord.ext import commands

log = logging.getLogger(__name__)

MOTIVATE_API_URL = "https://inspirobot.me/api?generate=true"
CATS_API_URL = "https://api.thecatapi.com/v1/images/search?limit=1"
DOGS_API_URL = "https://api.thedogapi.com/v1/images/search?limit=1"
DUCK_API_URL = "https://random-d.uk/api/v2/random"
FOX_API_URL = "https://randomfox.ca/floof/"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.http_session

    async def _fetch_json(self, url: str):
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def _send_picture(self, ctx: commands.Context, img_url: str):
        async with self.session.get(img_url) as resp:
            resp.raise_for_status()
            img = await resp.read()
        filename = "dagon" + _extension(img_url)
        await ctx.send(
            f"Dagon przygotował malowidło, {ctx.author.mention}:",
            file=discord.File(io.BytesIO(img), filename),
        )

    async def cog_command_error(self, ctx: commands.Context, error):
        original = getattr(error, "original", error)
        if isinstance(original, (aiohttp.ClientError, TimeoutError, KeyError)):
            log.warning("Fun command %s failed: %r", ctx.command, original)
            await ctx.send("Dagon nie zdołał dziś nic namalować. Spróbuj później.")
        else:
            raise error

    @commands.command(brief="Któż motywuje lepiej od Dagona?", aliases=["mot", "m"])
    async def motivate(self, ctx):
        async with ctx.typing():
            async with self.session.get(MOTIVATE_API_URL) as resp:
                resp.raise_for_status()
                img_url = (await resp.text()).strip()
            await self._send_picture(ctx, img_url)

    @commands.command(brief="Dagon jak wszyscy uwielbia kotki.")
    async def cat(self, ctx):
        async with ctx.typing():
            data = await self._fetch_json(CATS_API_URL)
            await self._send_picture(ctx, data[0]["url"])

    @commands.command(brief="Dagon uwielbia również pieski.")
    async def dog(self, ctx):
        async with ctx.typing():
            data = await self._fetch_json(DOGS_API_URL)
            await self._send_picture(ctx, data[0]["url"])

    @commands.command(brief="Dagon uwielbia malować kaczuszki.")
    async def duck(self, ctx):
        async with ctx.typing():
            data = await self._fetch_json(DUCK_API_URL)
            await self._send_picture(ctx, data["url"])

    @commands.command(brief="Dagon z przyjemnością namaluje Ci liska!")
    async def fox(self, ctx):
        async with ctx.typing():
            data = await self._fetch_json(FOX_API_URL)
            await self._send_picture(ctx, data["image"])


def _extension(url: str) -> str:
    path = url.split("?", 1)[0].lower()
    for ext in (".gif", ".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return ".png"


async def setup(bot):
    await bot.add_cog(Fun(bot))
