import discord
from discord.ext import commands

from yt import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        pass

    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.voice_client
        if voice_client:
            await ctx.send("Dagon has been banished!")
            await voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                ctx.voice_client.stop()

            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )
            ctx.voice_client.source.volume = self.bot.vol / 100

        await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    async def vol(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("You must be in a voice channel to talk to Dagon.")
        if volume > 100 or volume < 0:
            return await ctx.send("Volume must be in range (0-100).")
        self.bot.vol = volume
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client

        if voice_client:
            voice_client.stop()
            await ctx.send("Playback stopped.")
    
    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send(
                "Playback paused. Use !resume to continue or !play to play next track."
            )
        else:
            await ctx.send("Dagon is not currently playing any music.")

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Dagon is not currently paused.")

    @play.before_invoke
    @join.before_invoke
    async def ensure_voice(self, ctx):
        current_bot_channel = ctx.voice_client
        if current_bot_channel and current_bot_channel != ctx.author.voice:
            await current_bot_channel.disconnect()

        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            await ctx.send("Dagon has been summoned!")
        else:
            await ctx.send("You must be in a voice channel to summon Dagon.")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot):
    await bot.add_cog(Music(bot))
