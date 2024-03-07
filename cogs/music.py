import asyncio
from discord.ext import commands

from yt import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command(
        brief="Summon Dagon to your voice channel.",
        description="Dagon cannot be summoned to a channel if it has already been summoned to another voice channel.",
    )
    async def join(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                text = "Dagon is already in this channel, fool!"
            else:
                text = "Someone else has already summoned Dagon to another channel."
            return await ctx.send(text)
        await ctx.send("Dagon has been summoned!")
        await ctx.author.voice.channel.connect()

    @commands.command(brief="Banish Dagon from your voice channel.")
    async def leave(self, ctx):
        voice_client = ctx.voice_client
        if ctx.voice_client:
            await ctx.send("Dagon has been banished!")
            await voice_client.disconnect()

    @commands.command(
        brief="Play a song from YouTube. Use 'play loop <link>' to play song in loop.",
        description='Use "play <link>" to play music from a specific link or "play <title-of-song>" to search and play a song from YouTube. If Dagon is not in your voice channel, it will be summoned. If Dagon is already summoned in another voice channel, you cannot summon it.',
    )
    async def play(self, ctx, *, url: str = ""):
        if not url and not self.queue:
            return await ctx.send("You must provide a link or search term.")
        in_loop = False
        if url and url.split(" ")[0] == "loop":
            url = " ".join(url.split(" ")[1:])
            in_loop = True
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command("join"))
        if url:
            self.queue.insert(0, url)
        while self.queue:
            while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                await asyncio.sleep(2)
                pass
            try:
                async with ctx.typing():
                    player = await YTDLSource.from_url(self.queue.pop(0), loop=self.bot.loop)
                    ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                    ctx.voice_client.source.volume = self.bot.vol / 100
                await ctx.send(f'**Now playing:** {player.title}')
                if in_loop:
                    self.queue.insert(0, url)
            except:
                break

    @commands.command(brief="Add a song to the queue.")
    async def queue(self, ctx, *, url: str):
        self.queue.append(url)
        await ctx.send(f"Added to queue: {url}")

    @commands.command(brief="Print the current queue.")
    async def printqueue(self, ctx):
        if not self.queue:
            return await ctx.send("The queue is empty.")    
        await ctx.send("Current queue:")
        for i, song in enumerate(self.queue):
            await ctx.send(f"{i+1}. {song}") 

    @commands.command(brief="Clear the queue.")
    async def clearqueue(self, ctx):
        self.queue = []
        await ctx.send("Queue has been cleared.")

    @commands.command(brief="Change volume. Range (0-100).")
    async def vol(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("You must be in a voice channel to talk to Dagon.")
        if volume > 100 or volume < 0:
            return await ctx.send("Volume must be in range (0-100).")
        self.bot.vol = volume
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command(brief="Stop the current song.")
    async def stop(self, ctx):
        voice_client = ctx.voice_client

        if voice_client:
            voice_client.stop()
            self.queue = []
            await ctx.send("Playback stopped and queue is cleared.")

    @commands.command(brief="Pause the current song.")
    async def pause(self, ctx):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Dagon is not currently playing any music.")

    @commands.command(brief="Resume the paused song.")
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
        if not ctx.author.voice:
            await ctx.send("You must be in a voice channel to summon Dagon.")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot):
    await bot.add_cog(Music(bot))
