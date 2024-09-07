from discord.ext import commands
from discord.ext.commands.context import Context
from yt_dlp.utils import DownloadError

from yt import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Wykonaj rytual przyzywania Dagona.",
        aliases=["j"]
    )
    async def join(self, ctx: Context):
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                text = "Dagon już przebywa wśród Was!"
            else:
                text = "Dagon został przyzwany przez kogoś innego."
            return await ctx.send(text)
        await ctx.send("Lękajcie się śmiertelnicy, oto nadchodzi Przedwieczny Dagon!")
        await ctx.author.voice.channel.connect()

    @commands.command(brief="Wykonaj rytuał odesłania Dagon do jego wymiaru z nadzieją ze się powiedzie.", aliases=["l"])
    async def leave(self, ctx: Context):
        voice_client = ctx.voice_client
        if ctx.voice_client:
            await ctx.send("Tym razem udało się odesłać Dagona...")
            await voice_client.disconnect()

    @commands.command(
        brief="Zmuś przedwiecznego do odegrania pieśni z Youtube.",
        description='Uzyj linku do konkretnego utworu bądź podaj frazę po której Dagon wyszuka utworu na YT.',
        aliases=["p"],
    )
    async def play(self, ctx, *, url: str = ""):
        if not url:
            return await ctx.send("Podaj link lub frazę jeżeli nie chcesz rozsłościć Dagona...")
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
            await ctx.send(f"**Dagon zaśpiewa Wam:** {player.title}")
        except DownloadError as e:
            await ctx.send(f"Niech to Cthulhu strzeli, YouTube nie współpracuje : {e}")
        except Exception as e:
            print(f"bład: {e}")
            await ctx.send(f"Zadziało się coś nieoczekiwanego: {e}")

    @commands.command(brief="Ustaw głośność Dagona w przedziale 0-100.")
    async def vol(self, ctx: Context, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Żeby to zrobić musisz być na kanale głosowym.")
        if volume > 100 or volume < 0:
            return await ctx.send("Podaj liczbę w przedziale 0-100.")
        self.bot.vol = volume
        if ctx.voice_client.source.volume * 100 > volume:
            text = "Dagon postara się być ciszej"
        else:
            text = "Dagon będzie śpiewać głośniej"
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(text)

    @commands.command(brief="Poproś Dagona aby skończył już spiewać (ryzykowne).", aliases=["s"])
    async def stop(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client:
            voice_client.stop()
            await ctx.send("Tym razem Dagon posłuchał i przestał śpiewać.")

    @commands.command(brief="Poproś o którką przerwę.")
    async def pause(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Dagon zgodził się przerwac na chwilę.")
        else:
            await ctx.send("Dagon spojrzał na Ciebie zdegustowany. Przecież obecnie nic nie śpiewa.")

    @commands.command(brief="Resume the paused song.", aliases=["r"])
    async def resume(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Dagon wznawia swój śpiew.")
        else:
            await ctx.send("Czujesz na sobie wwieracjące się spojrzenie Dagona - przecież nie ma czego wznawiać.")

    @play.before_invoke
    @join.before_invoke
    async def ensure_voice(self, ctx: Context):
        if not ctx.author.voice:
            await ctx.send("Musisz znajdować się w kręgu przywołań (kanale głosowym)")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot: commands.Bot):
    await bot.add_cog(Music(bot))
