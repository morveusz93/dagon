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

    @commands.command(brief="Dagon pomoże wymyśleć Ci nowe imię.")
    async def name(self, ctx):
        resp = requests.post(NAME_API_URL)
        name = resp.json()["results"][0]
        author = ctx.author
        await ctx.send(
            f"Od dziś, {author.mention} będzie znana / znany jako: **{name.capitalize()}**"
        )

    @commands.command(
        brief="Poproś Dagona o wymyślenie nazwy dla miasta, gildii, kontynenty czy... czegokolwiek.",
        description="Dostępne kategorie: Guild, Magic, Tavern, Inn, Shop, Town, City, Country, Kingdom, Lake, Mountain, Forest, Island, Continent, World, Planet",
    )
    async def placenames(
        self,
        ctx,
        cat: str = "",
    ):
        cat = cat.capitalize()
        if cat not in PLACENAMES_CATEGORIES:
            await ctx.send(
                f"Dagon nie zna tej kategorii, poda Ci nazwy z losowych."
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
        await ctx.send(f"Twoje zamówienie, {ctx.author.mention}: \n{result}")


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
