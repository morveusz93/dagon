from discord.ext import commands
from discord.ext.commands.context import Context
from yt_dlp.utils import DownloadError

from yt import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Summon Dagon to your voice channel.",
        description="Dagon cannot be summoned to a channel if it has already been summoned to another voice channel.",
    )
    async def join(self, ctx: Context):
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                text = "Dagon is already here!"
            else:
                text = "Someone else has already summoned Dagon to another channel."
            return await ctx.send(text)
        await ctx.send("Dagon has been summoned!")
        await ctx.author.voice.channel.connect()

    @commands.command(brief="Banish Dagon from your voice channel.")
    async def leave(self, ctx: Context):
        voice_client = ctx.voice_client
        if ctx.voice_client:
            await ctx.send("Dagon has been banished!")
            await voice_client.disconnect()

    @commands.command(
        brief="Play a song from YouTube.",
        description='Use "play <link>" to play music from a specific link or "play <title-of-song>" to search and play a song from YouTube.',
        aliases=["p"],
    )
    async def play(self, ctx, *, url: str = ""):
        if not url:
            return await ctx.send("Nothing to play...")
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command("join"))
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            return
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
            )
            ctx.voice_client.source.volume = self.bot.vol / 100
            await ctx.send(f"**Now playing:** {player.title}")
        except DownloadError as e:
            await ctx.send(f"Youtube Error: {e}")
        except Exception as e:
            print(f"bład: {e}")
            await ctx.send(f"Wystąpił nieoczekiwany błąd: {e}")

    @commands.command(brief="Change volume. Range (0-100).")
    async def vol(self, ctx: Context, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("You must be in a voice channel to talk to Dagon.")
        if volume > 100 or volume < 0:
            return await ctx.send("Volume must be in range (0-100).")
        self.bot.vol = volume
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(brief="Stop the current song.", aliases=["s"])
    async def stop(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client:
            voice_client.stop()
            await ctx.send("Playback stopped.")

    @commands.command(
        brief="Stop the current song.", aliases=["sa"]
    )
    async def stopall(self, ctx: Context):
        voice_client = ctx.voice_client
        if voice_client:
            voice_client.stop()
            await ctx.send("Playback stopped.")

    @commands.command(brief="Pause the current song.")
    async def pause(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Dagon is not currently playing any music.")

    @commands.command(brief="Resume the paused song.")
    async def resume(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Dagon is not currently paused.")

    @play.before_invoke
    @join.before_invoke
    async def ensure_voice(self, ctx: Context):
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel to summon Dagon.")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot: commands.Bot):
    await bot.add_cog(Music(bot))
