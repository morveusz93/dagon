import random
import re
from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands

import style
from errors import DagonError

MAX_DICE = 100  # łącznie we wszystkich grupach
MAX_SIDES = 100
MAX_TERMS = 10
MAX_MODIFIER = 1000

TERM = re.compile(r"([+-])?(?:(\d*)[dk](\d+)|(\d+))")
ERROR_MSG = (
    "Podaj rzut, np. `3d6`, `d20+5` albo `2d6+1d4-1`. "
    f"Dagon rzuci maksymalnie {MAX_DICE} kośćmi naraz, każda do {MAX_SIDES} ścianek."
)


@dataclass(frozen=True)
class DiceGroup:
    count: int
    sides: int
    sign: int = 1

    def __str__(self) -> str:
        return f"{self.count}d{self.sides}"


@dataclass(frozen=True)
class RollSpec:
    groups: tuple[DiceGroup, ...]
    modifier: int = 0

    def __str__(self) -> str:
        parts = [("+ " if g.sign > 0 else "− ") + str(g) for g in self.groups]
        if self.modifier:
            parts.append(
                ("+ " if self.modifier > 0 else "− ") + str(abs(self.modifier))
            )
        text = " ".join(parts)
        return text[2:] if text.startswith("+ ") else text


class Rpg(commands.Cog, description="🎲 Kości"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        description="Rzut kośćmi z modyfikatorami, np. 3d6, d20+5, 2d6+1d4-1."
    )
    @app_commands.describe(rzut="Np. 3d6 (trzy kości sześciościenne), d20+5, 2d6+1d4-1")
    async def roll(self, ctx: commands.Context, *, rzut: str):
        try:
            spec = parse_roll(rzut)
        except ValueError:
            raise DagonError(ERROR_MSG) from None
        results = roll_dice(spec)
        await ctx.send(embed=roll_embed(ctx.author.mention, spec, results))


def parse_roll(text: str) -> RollSpec:
    """Parse e.g. '2d6 + 1d4 - 1' / '3k6' / 'd20+5' into a RollSpec."""
    # spacje dozwolone tylko wokół znaków, "1d6 2" to błąd, a nie 1d62
    s = re.sub(r"\s*([+-])\s*", r"\1", text.strip().lower())
    groups: list[DiceGroup] = []
    modifier = 0
    pos = 0
    terms = 0
    while pos < len(s):
        match = TERM.match(s, pos)
        sign_char = match.group(1) if match else None
        # pierwszy wyraz bez znaku, każdy kolejny ze znakiem
        if not match or (terms == 0) == (sign_char is not None):
            raise ValueError(f"Invalid roll: {text!r}")
        sign = -1 if sign_char == "-" else 1
        count, sides, const = match.group(2, 3, 4)
        if const is not None:
            modifier += sign * int(const)
        else:
            group = DiceGroup(int(count or 1), int(sides), sign)
            if not (group.count >= 1 and 1 <= group.sides <= MAX_SIDES):
                raise ValueError(f"Dice out of range: {text!r}")
            groups.append(group)
        terms += 1
        pos = match.end()

    if not groups:
        raise ValueError(f"No dice in roll: {text!r}")
    if terms > MAX_TERMS or sum(g.count for g in groups) > MAX_DICE:
        raise ValueError(f"Roll too big: {text!r}")
    if abs(modifier) > MAX_MODIFIER:
        raise ValueError(f"Modifier too big: {text!r}")
    return RollSpec(tuple(groups), modifier)


def signed(n: int) -> str:
    return f"+{n}" if n >= 0 else f"−{abs(n)}"


def roll_dice(spec: RollSpec) -> list[list[int]]:
    return [[random.randint(1, g.sides) for _ in range(g.count)] for g in spec.groups]


def total(spec: RollSpec, results: list[list[int]]) -> int:
    return (
        sum(g.sign * sum(rolls) for g, rolls in zip(spec.groups, results))
        + spec.modifier
    )


def format_rolls(rolls: list[int], sides: int) -> str:
    """Każdy wynik jako kafelek; jedynka z czaszką, maksimum z gwiazdką."""

    def fmt(roll: int) -> str:
        tile = f"`{roll}`"
        if roll == sides:
            return tile + "⭐"
        if roll == 1:
            return tile + "💀"
        return tile

    return "  ".join(fmt(r) for r in rolls)


def roll_embed(mention: str, spec: RollSpec, results: list[list[int]]) -> discord.Embed:
    lines = [f"{mention} rzuca **{spec}**", ""]
    if len(spec.groups) == 1:
        lines.append(format_rolls(results[0], spec.groups[0].sides))
    else:
        for group, rolls in zip(spec.groups, results):
            label = ("−" if group.sign < 0 else "") + str(group)
            lines.append(f"**{label}:** {format_rolls(rolls, group.sides)}")
    if spec.modifier:
        lines.append(f"Modyfikator: **{signed(spec.modifier)}**")

    dice_count = sum(len(r) for r in results)
    if dice_count > 1 or spec.modifier:
        lines += ["", f"Suma: **{total(spec, results)}**"]
    return style.embed("\n".join(lines), title="🎲 Rzut kośćmi")


async def setup(bot):
    await bot.add_cog(Rpg(bot))
