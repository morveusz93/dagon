import io

import aiohttp
import discord
import requests
from discord.ext import commands


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Hey, kid! Do you want some motivation?")
    async def motivate(self, ctx):
        url = "https://inspirobot.me/api?generate=true"
        resp = requests.get(url)
        img_url = resp.content.decode("utf-8")
        async with aiohttp.ClientSession() as session:
            async with session.get(img_url) as resp:
                img = await resp.read()
                with io.BytesIO(img) as file:
                    await ctx.send(file=discord.File(file, "BestMotivation.png"))


async def setup_others(bot):
    await bot.add_cog(Others(bot))
