import datetime as dt
import hashlib
import logging
import re
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

import style

log = logging.getLogger(__name__)

# "winiary" zapisane dowolnie (winiary, Winiary, WiNiArY...) - bez odmiany
WINIARY = re.compile(r"\bwiniary\b", re.IGNORECASE)
REACTION = "🤮"

TIMEZONE = ZoneInfo("Europe/Warsaw")

# Majonez -> możliwe orzeczenia Dagona
MAYONNAISES = {
    "Kielecki": [
        "Głębiny przemówiły jasno. Dziś Kielecki.",
        "Nawet macki Dagona drżą z zachwytu. Kielecki.",
        "Kielecki. Dagon nie przyjmuje odwołań.",
    ],
    "Winiary": [
        "Dagon sprawdził trzy razy. Niestety wyszło Winiary. 🤮",
        "Gwiazdy ułożyły się źle. Dziś Winiary. Dagon odchodzi w głębiny.",
        "Winiary. Dagon nie chce o tym rozmawiać.",
    ],
    "Motyl": [
        "Dziś skrzydła rozwinął Motyl. Dagon jest zaskoczony nie mniej niż Ty.",
        "Motyl. Cichy faworyt głębin.",
    ],
    "Kętrzyński": [
        "Z mgieł Warmii wyłania się Kętrzyński.",
        "Kętrzyński. Dagon szanuje odwagę wyznawców.",
    ],
    "Roleski": [
        "Roleski wynurza się z głębin. Dagon kiwa macką z uznaniem.",
        "Dziś Roleski. Stara gwardia musi ustąpić.",
    ],
    "Hellmann's": [
        "Hellmann's. Zza oceanu przypłynęło coś obcego. Dagon obserwuje.",
        "Dziś Hellmann's. Głębiny tolerują przybysza. Na razie.",
    ],
    "Pomorski Ocetix": [
        "Fale Bałtyku przyniosły Pomorski Ocetix. Dagon czuje się jak w domu.",
        "Pomorski Ocetix. Morze zawsze wie najlepiej.",
        "Dziś Pomorski Ocetix. Głębiny pozdrawiają Pomorze.",
    ],
}


class Mayo(commands.Cog, description="🥚 Majonez"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Majonez dnia według Dagona.")
    async def majonez(self, ctx: commands.Context):
        day = today()
        guild_id = ctx.guild.id if ctx.guild else 0
        name, verdict = mayo_of_the_day(day, guild_id)
        embed = style.embed(
            f"Dzisiejszym majonezem jest **{name}**.\n\n*{verdict}*",
            title="🥚 Majonez dnia",
        )
        embed.set_footer(text=day.strftime("%d.%m.%Y"))
        await ctx.send(embed=embed)

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


def today() -> dt.date:
    return dt.datetime.now(TIMEZONE).date()


def mayo_of_the_day(day: dt.date, guild_id: int) -> tuple[str, str]:
    """Ten sam wynik przez cały dzień na danym serwerze - bez zapisywania stanu."""
    digest = hashlib.sha256(f"{day.isoformat()}:{guild_id}".encode()).digest()
    seed = int.from_bytes(digest[:8], "big")
    names = list(MAYONNAISES)
    name = names[seed % len(names)]
    verdicts = MAYONNAISES[name]
    return name, verdicts[(seed // len(names)) % len(verdicts)]


async def setup(bot):
    await bot.add_cog(Mayo(bot))
