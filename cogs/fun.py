import asyncio
import io
import logging
import random
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
# iNaturalist: obserwacje z potwierdzonym gatunkiem i zdjęciami na wolnych
# licencjach. order_by=random jest ignorowane, więc losujemy stronę - API pozwala
# sięgnąć najwyżej do 10 000. wyniku.
INAT_API_URL = (
    "https://api.inaturalist.org/v1/observations?taxon_id={taxon}&photos=true"
    "&quality_grade=research&photo_license=cc0,cc-by,cc-by-sa&per_page=1&page={page}"
)
INAT_MAX_PAGE = 10_000
INAT_LICENSES = {"cc0", "cc-by", "cc-by-sa"}
OWLS = 19350  # rząd Strigiformes
HEDGEHOGS = 846194  # podrodzina Erinaceinae
OTTERS = 526556  # podrodzina Lutrinae
CAPYBARAS = 71855  # rodzaj Hydrochoerus
SEALS = 41687  # rodzina Phocidae (foki właściwe)

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
        # taxon_id -> liczba obserwacji, żeby nie losować pustych stron
        self._inat_totals: dict[int, int] = {}

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
        get_url: Callable[[], Awaitable[str | tuple[str, str]]],
    ):
        """get_url zwraca adres obrazka albo (adres, podpis do stopki)."""
        async with ctx.typing():
            try:
                result = await get_url()
                img_url, footer = (
                    result if isinstance(result, tuple) else (result, None)
                )
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
            if footer:
                embed.set_footer(text=footer)
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

    async def _inat_photo(self, taxon: int) -> tuple[str, str]:
        # Pierwsze wywołanie bierze stronę 1 i zapamiętuje, ile jest wyników
        pages = min(self._inat_totals.get(taxon, 1), INAT_MAX_PAGE)
        page = random.randint(1, pages)
        data = await self._json_field(INAT_API_URL.format(taxon=taxon, page=page))
        self._inat_totals[taxon] = data["total_results"]
        observation = data["results"][0]
        photo = next(
            (
                p
                for p in observation["photos"]
                if p.get("license_code") in INAT_LICENSES
            ),
            None,
        )
        if photo is None:
            raise ValueError("observation has no freely licensed photo")
        taxon_info = observation["taxon"]
        species = taxon_info.get("preferred_common_name") or taxon_info["name"]
        # Domyślny adres to miniaturka 75 px
        url = photo["url"].replace("/square.", "/large.")
        return url, f"{species} · {photo['attribution']}"

    async def _paint_inat(self, ctx: commands.Context, title: str, taxon: int):
        await self._paint(ctx, title, lambda: self._inat_photo(taxon))

    @commands.hybrid_command(description="Dagon namaluje Ci mądrą sówkę.")
    async def owl(self, ctx):
        await self._paint_inat(ctx, "🦉 Sówka", OWLS)

    @commands.hybrid_command(description="Dagon namaluje Ci kolczastego jeżyka.")
    async def hedgehog(self, ctx):
        await self._paint_inat(ctx, "🦔 Jeżyk", HEDGEHOGS)

    @commands.hybrid_command(description="Dagon namaluje Ci wydrę, kuzynkę z głębin.")
    async def otter(self, ctx):
        await self._paint_inat(ctx, "🦦 Wydra", OTTERS)

    @commands.hybrid_command(description="Dagon namaluje Ci niewzruszoną kapibarę.")
    async def capybara(self, ctx):
        await self._paint_inat(ctx, "🐾 Kapibara", CAPYBARAS)

    @commands.hybrid_command(description="Dagon namaluje Ci foczkę prosto z morza.")
    async def seal(self, ctx):
        await self._paint_inat(ctx, "🦭 Foczka", SEALS)


def _extension(url: str) -> str:
    path = url.split("?", 1)[0].lower()
    for ext in (".gif", ".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return ".png"


async def setup(bot):
    await bot.add_cog(Fun(bot))
