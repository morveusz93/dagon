import io

import aiohttp
import discord
import requests
from discord.ext import commands


MOTIVATE_API_URL = "https://inspirobot.me/api?generate=true"
CATS_API_URL = "https://api.thecatapi.com/v1/images/search?limit=1"
DOGS_API_URL = "https://api.thedogapi.com/v1/images/search?limit=1"
DUCK_API_URL = "https://random-d.uk/api/v2/random"
FOX_API_URL = "https://randomfox.ca/floof/"
UNSPLASH_URL = "https://source.unsplash.com/random/?"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Hey, kid, want some motivation?")
    async def motivate(self, ctx):
        resp = requests.get(MOTIVATE_API_URL)
        img_url = resp.content.decode("utf-8")
        await send_picture(img_url, ctx)

    @commands.command(
        brief="A little cat for you.",
        description='You have to type number of dices, then "k" and dice you wan to roll, eg. 1k10, 2k100, 3d20, d2, k4',
    )
    async def cat(self, ctx):
        resp = requests.get(CATS_API_URL)
        img_url = resp.json()[0]["url"]
        await send_picture(img_url, ctx)

    @commands.command(brief="A cute dog will make your day better.")
    async def dog(self, ctx):
        resp = requests.get(DOGS_API_URL)
        img_url = resp.json()[0]["url"]
        await send_picture(img_url, ctx)

    @commands.command(brief="Kwa Kwa mother fucker!")
    async def duck(self, ctx):
        resp = requests.get(DUCK_API_URL)
        img_url = resp.json()["url"]
        await send_picture(img_url, ctx)

    @commands.command(brief="Cool fox!")
    async def fox(self, ctx):
        resp = requests.get(FOX_API_URL)
        img_url = resp.json()["image"]
        await send_picture(img_url, ctx)

    @commands.command(brief="Random picture of anything you type.")
    async def pic(self, ctx, *args):
        img_url = UNSPLASH_URL + ",".join(args)
        await send_picture(img_url, ctx)


async def send_picture(img_url, ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            img = await resp.read()
            with io.BytesIO(img) as file:
                await ctx.send(f"Your order, {ctx.author.mention}:", file=discord.File(file, "yourpic.png"))


async def setup_fun(bot):
    await bot.add_cog(Fun(bot))
