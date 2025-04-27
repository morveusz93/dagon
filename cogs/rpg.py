import random

import requests
from discord.ext import commands


class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Poproś Dagona o rzut kośćmi. Dagon posiada po 100 kości od tych z jednym oczkiem do tych ze 100 oczkami. Podaj liczbę kości i ich rodzaj, np 1d10"
    )
    async def roll(self, ctx, dices: str):
        error_msg = "Błędna komenda. Podaj liczbę kości i ich rodzaj, np 1d10"
        cmd = get_command_from_dices(dices)
        if not cmd or len(cmd) > 2:
            return await ctx.send(error_msg)
        try:
            dice, number_of_dices = get_dices(cmd)
        except ValueError:
            return await ctx.send(error_msg)
        rolls = roll_dices(number_of_dices, dice)
        return await ctx.send(f"{ctx.author.mention}: {rolls}")


async def setup_rpg(bot):
    await bot.add_cog(Rpg(bot))


def roll_dices(number_of_dices: int, dice: int) -> str:
    rolls = [random.randint(1, dice) for _ in range(number_of_dices)]
    result = ""
    for roll in rolls:
        if roll == 1:
            result += "*1* "
        elif roll == dice:
            result += f"**{roll}** "
        else:
            result += f"{roll} "
    result += f" = {sum(rolls)}"
    return result.strip()


def get_command_from_dices(dices):
    dices = dices.lower()
    if "k" in dices:
        return dices.split("k")
    elif "d" in dices:
        return dices.split("d")


def get_dices(cmd):
    number_of_dices = 1
    dice = int(cmd[-1])
    if cmd[0]:
        number_of_dices = int(cmd[0])
    if dice > 100 or number_of_dices > 100:
        raise ValueError("Too big number")
    return dice, number_of_dices
