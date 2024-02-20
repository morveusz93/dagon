import io
import random

import aiohttp
import discord
import requests
from discord.ext import commands


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Hey, kid, want some motivation?")
    async def motivate(self, ctx):
        url = "https://inspirobot.me/api?generate=true"
        resp = requests.get(url)
        img_url = resp.content.decode("utf-8")
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "BestMotivation.png"))

    @commands.command(
        brief="A little cat for you.",
        description='You have to type number of dices, then "k" and dice you wan to roll, eg. 1k10, 2k100, 3d20, d2, k4',
    )
    async def cat(self, ctx):
        url = "https://api.thecatapi.com/v1/images/search?limit=1"
        resp = requests.get(url)
        img_url = resp.json()[0]["url"]
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "cat4u.png"))

    @commands.command(brief="A cute dog will make your day better.")
    async def dog(self, ctx):
        url = "https://api.thedogapi.com/v1/images/search?limit=1"
        resp = requests.get(url)
        img_url = resp.json()[0]["url"]
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "cat4u.png"))

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
        url = 'https://chartopia.d12dev.com/api/charts/19/roll/'
        resp = requests.post(url)
        name = resp.json()['results'][0]
        author = ctx.author
        await ctx.send(f"From this day forward {author.mention} will be known as **{name.capitalize()}**")


async def setup_others(bot):
    await bot.add_cog(Others(bot))


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
