import time
from discord import ClientException
from discord.ext import commands
from discord.ext.commands.context import Context
from yt_dlp.utils import DownloadError

from music_queue import MusicQueue
from yt import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_queue = MusicQueue()
        self.is_looping = False

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
            self.music_queue.clear()

    async def play_next(self, ctx):
        try:
            if self.music_queue.is_empty():
                return await ctx.send("The queue is now empty.")
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                return
            player = await YTDLSource.from_url(self.music_queue.get())
            ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            ctx.voice_client.source.volume = self.bot.vol / 100
            await ctx.send(f'**Now playing:** {player.title}')
            if not self.is_looping:
                self.music_queue.remove_first()
        except Exception as e:
            print(f"bład: {e}")
            await ctx.send(f"Wystąpił nieoczekiwany błąd: {e}")

    @commands.command(
        brief="Play a song from YouTube.",
        description='Use "play <link>" to play music from a specific link or "play <title-of-song>" to search and play a song from YouTube.',
        aliases=['p'],
    )
    async def play(self, ctx, *, url: str = ""):
        if not url and self.music_queue.is_empty():
            return await ctx.send("Nothing to play...")

        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command("join"))
        if url:
            await self._prepare_queue(url, ctx)
        await self.play_next(ctx)

    async def _prepare_queue(self, url:str, ctx: Context):
        await ctx.send(f"Getting music from youtube...")
        try:
            entries = await YTDLSource.get_audio_entries(url, loop=self.bot.loop)
        except DownloadError as e:
            await ctx.send(f"Youtube Error: {e}")
        for entry in entries:
            self.music_queue.add(entry)
            await ctx.send(f"Added to queue: {entry.title}")

    @commands.command(
        brief="Loop the current or next song.",
        description="Enables looping of the currently playing or the next song if nothing is playing.",
        aliases=['l']
    )
    async def loop(self, ctx):
        if self.is_looping:
            return await ctx.send("There is already loop set.")
        looping_song = self.music_queue.get_last_song()
        if not looping_song:
            return await ctx.send("There is no song to loop.")
        self.is_looping = True
        self.music_queue.skip_queue(looping_song)
        await ctx.send(f"Looping {looping_song.title}")

    @commands.command(
        brief="Stop looping the song.",
        description="Disables the looping of the current song.",
        aliases=["sl"]
    )
    async def stoploop(self, ctx):
        if self.is_looping:
            self.is_looping = False
            looped_song = self.music_queue.remove_first()
            return await ctx.send(f"Stopped looping: {looped_song.title}.")
        return await ctx.send("There is no looping set.")

    @commands.command(brief="Add a song to the queue.", aliases=['q'])
    async def queue(self, ctx: Context, *, url: str):
        try:
            await self._prepare_queue(url, ctx)
        except Exception as e:
            print(e)

    @commands.command(brief="Print the current queue.", aliases=['pq'])
    async def printqueue(self, ctx: Context):
        try:
            if self.music_queue.is_empty():
                return await ctx.send("The queue is empty.")    
            await ctx.send("Current queue:")
            queue = self.music_queue.get_all()
            for i, song in enumerate(queue):
                await ctx.send(f"{i+1}. {song.title}")
        except Exception as e:
            print(e)

    @commands.command(brief="Clear the queue.", aliases=['cq'])
    async def clearqueue(self, ctx: Context):
        self.music_queue.clear()
        await ctx.send("Queue has been cleared.")

    @commands.command(brief="Print the history.", aliases=['ph'])
    async def printhistory(self, ctx: Context):
        try:
            history = self.music_queue.get_history()
            if not history:
                return await ctx.send("The history is empty.")    
            await ctx.send("History of songs:")
            for i, song in enumerate(history):
                await ctx.send(f"{i+1}. {song.title}")
        except Exception as e:
            print(e)

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

    @commands.command(brief="Stop the current song and clear the queue.", aliases=["sa"])
    async def stopall(self, ctx: Context):
        voice_client = ctx.voice_client
        if voice_client:
            self.music_queue.clear()
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
