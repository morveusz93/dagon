import random
import re

import discord
from discord import app_commands
from discord.ext import commands

import style
from errors import DagonError

MAX_DICE = 100
MAX_SIDES = 100
DICE_PATTERN = re.compile(r"^(\d*)[dk](\d+)$")
ERROR_MSG = (
    "Podaj liczbę kości i ich rodzaj, np. `3d6`, `d20` albo `2k10`. "
    f"Dagon rzuci maksymalnie {MAX_DICE} kośćmi naraz, każda do {MAX_SIDES} ścianek."
)


class Rpg(commands.Cog, description="🎲 Kości"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Rzut kośćmi, np. 3d6, d20 albo 2k10.")
    @app_commands.describe(kosci="Np. 3d6, d20 albo 2k10")
    async def roll(self, ctx: commands.Context, kosci: str):
        try:
            count, sides = parse_dice(kosci)
        except ValueError:
            raise DagonError(ERROR_MSG) from None
        rolls = [random.randint(1, sides) for _ in range(count)]
        await ctx.send(embed=roll_embed(ctx.author.mention, count, sides, rolls))


def parse_dice(text: str) -> tuple[int, int]:
    """Parse '3d6' / '3k6' / 'd20' into (count, sides)."""
    match = DICE_PATTERN.match(text.strip().lower())
    if not match:
        raise ValueError(f"Invalid dice: {text!r}")
    count = int(match.group(1) or 1)
    sides = int(match.group(2))
    if not (1 <= count <= MAX_DICE and 1 <= sides <= MAX_SIDES):
        raise ValueError(f"Dice out of range: {text!r}")
    return count, sides


def format_rolls(rolls: list[int], sides: int) -> str:
    """Jedynki kursywą, maksima pogrubione."""

    def fmt(roll: int) -> str:
        if roll == 1:
            return "*1*"
        if roll == sides:
            return f"**{roll}**"
        return str(roll)

    return " · ".join(fmt(r) for r in rolls)


def roll_embed(mention: str, count: int, sides: int, rolls: list[int]) -> discord.Embed:
    description = f"{mention} rzuca **{count}d{sides}**\n\n{format_rolls(rolls, sides)}"
    if len(rolls) > 1:
        description += f"\n\nSuma: **{sum(rolls)}**"
    return style.embed(description, title="🎲 Rzut kośćmi")


async def setup(bot):
    await bot.add_cog(Rpg(bot))
