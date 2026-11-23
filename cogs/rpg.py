import random
import re

from discord.ext import commands

MAX_DICE = 100
MAX_SIDES = 100
DICE_PATTERN = re.compile(r"^(\d*)[dk](\d+)$")
ERROR_MSG = "Błędna komenda. Podaj liczbę kości i ich rodzaj, np. 1d10 lub 3k6."


class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Poproś Dagona o rzut kośćmi, np. 1d10 albo 3k6.",
        description=(
            f"Dagon posiada po {MAX_DICE} kości od tych z jednym oczkiem "
            f"do tych z {MAX_SIDES} oczkami. Podaj liczbę kości i ich rodzaj, np. 1d10."
        ),
    )
    async def roll(self, ctx, dice: str = ""):
        try:
            count, sides = parse_dice(dice)
        except ValueError:
            return await ctx.send(ERROR_MSG)
        rolls = [random.randint(1, sides) for _ in range(count)]
        await ctx.send(f"{ctx.author.mention}: {format_rolls(rolls, sides)}")


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
    def fmt(roll: int) -> str:
        if roll == 1:
            return "*1*"
        if roll == sides:
            return f"**{roll}**"
        return str(roll)

    result = " ".join(fmt(r) for r in rolls)
    if len(rolls) > 1:
        result += f" = {sum(rolls)}"
    return result


async def setup(bot):
    await bot.add_cog(Rpg(bot))
