import random

import requests
from discord.ext import commands

NAME_API_URL = "https://chartopia.d12dev.com/api/charts/19/roll/"
PLACENAME_API_URL = (
    "https://codexnomina.com/wp-admin/admin-ajax.php?action=return_generate"
)
PLACENAME_HEADERS = {
    "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}
PLACENAMES_CATEGORIES = [
    "",
    "Guild",
    "Magic",
    "Tavern",
    "Inn",
    "Shop",
    "Town",
    "City",
    "Country",
    "Kingdom",
    "Lake",
    "Mountain",
    "Forest",
    "Island",
    "Continent",
    "World",
    "Planet",
]


class Rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Roll a dice[s]. Type '!droll 2k10' or '!droll 1d100'. Max number of dices is 100, biggest dice is 100 also."
    )
    async def roll(self, ctx, dices: str):
        error_msg = "Wrong command. Type <number_of_dices>K<dice_type>, eg 2k10."
        cmd = get_command_from_dices(dices)
        if not cmd or len(cmd) > 2:
            return await ctx.send(error_msg)
        try:
            dice, number_of_dices = get_dices(cmd)
        except ValueError:
            return await ctx.send(error_msg)
        rolls = roll_dices(number_of_dices, dice)
        return await ctx.send(f"{ctx.author.mention}: {rolls}")

    @commands.command(brief="Get new name.")
    async def name(self, ctx):
        resp = requests.post(NAME_API_URL)
        name = resp.json()["results"][0]
        author = ctx.author
        await ctx.send(
            f"From this day forward {author.mention} will be known as **{name.capitalize()}**"
        )

    @commands.command(brief="Get new name.")
    async def placenames(
        self,
        ctx,
        cat: str = commands.parameter(
            default="",
            description="Avaiable categories: Guild, Magic, Tavern, Inn, Shop, Town, City, Country, Kingdom, Lake, Mountain, Forest, Island, Continent, World, Planet",
        ),
    ):
        cat = cat.capitalize()
        if cat not in PLACENAMES_CATEGORIES:
            await ctx.send(
                f"Sorry {ctx.author.mention}, I don't recognize this category. I will search in all categories."
            )
            cat = ""

        data = {
            "post_id": "2307",
            "filter_1": cat,
        }
        response = requests.post(
            PLACENAME_API_URL, headers=PLACENAME_HEADERS, data=data
        )
        names = (
            response.content.decode("utf-8")
            .replace("<p>", "")
            .replace("</p>", ", ")
            .split(",")
        )
        result = "\n".join(["**" + n.strip() + "**" for n in names if n != " "])
        await ctx.send(f"Your order, {ctx.author.mention}: \n{result}")


async def setup_rpg(bot):
    await bot.add_cog(Rpg(bot))


def roll_dices(number_of_dices, dice):
    rolls = [random.randint(1, dice) for _ in range(number_of_dices)]
    result = ""
    for roll in rolls:
        if roll == 1:
            result += "*1* "
        elif roll == dice:
            result += f"**{roll}** "
        else:
            result += f"{roll} "
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
