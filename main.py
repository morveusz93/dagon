import asyncio
from config import ytdl_format_options, ffmpeg_options
import discord
import yt_dlp as youtube_dl

from discord.ext import commands
import os

from dagon import Dagon

TOKEN = os.getenv("DISCORD_TOKEN")

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]

        audio_url = data['url']
        return cls(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        await ctx.send("Dagon has been summoned!")

    @commands.command()
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            ctx.voice_client.source.volume = self.bot.vol / 100

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def vol(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        if volume > 100 or volume < 0:
            return await ctx.send("Volume must be in range (0-100).")
        self.bot.vol = volume
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice_client:
            voice_client.stop()
            await ctx.send("Playback stopped.")

    @play.before_invoke
    @join.before_invoke
    async def ensure_voice(self, ctx):
        current_bot_channel = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if current_bot_channel and current_bot_channel != ctx.author.voice:
            await current_bot_channel.disconnect()

        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")


async def main():
    bot = Dagon()
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(TOKEN)


asyncio.run(main())
