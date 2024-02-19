import io

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


    @commands.command(brief="A little cat for you.")
    async def cat(self, ctx):
        url = "https://api.thecatapi.com/v1/images/search?limit=1"
        resp = requests.get(url)
        img_url = resp.json()[0]['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "cat4u.png"))


    @commands.command(brief="A cute dog will make your day better.")
    async def dog(self, ctx):
        url = "https://api.thedogapi.com/v1/images/search?limit=1"
        resp = requests.get(url)
        img_url = resp.json()[0]['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "cat4u.png"))

async def setup_others(bot):
    await bot.add_cog(Others(bot))
