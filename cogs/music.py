import asyncio

import discord
import wavelink
from discord.ext import commands
from discord.ext.commands.context import Context
from dagon import Dagon


class Music(commands.Cog):
    def __init__(self, bot: Dagon):
        self.bot = bot

    @commands.hybrid_command(name="join", brief="Wykonaj rytuał przyzywania Dagona.")
    async def _connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel | None = None):
        print("Przyzywanie")
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                text = "Dagon już przebywa wśród Was!"
            else:
                text = "Dagon został przyzwany przez kogoś innego."
            return await ctx.send(text)
        channel = channel or ctx.author.voice.channel
        print(f"Channel: {channel}")
        player: wavelink.Player = await channel.connect(cls=wavelink.Player)
        print(f"Player: {player}")
        await ctx.send("Lękajcie się śmiertelnicy, oto nadchodzi Przedwieczny Dagon!")
        return player

    @commands.command(brief="Wykonaj rytuał odesłania Dagon do jego wymiaru z nadzieją ze się powiedzie.", aliases=["l"])
    async def leave(self, ctx: Context):
        voice_client = ctx.voice_client
        if ctx.voice_client:
            await ctx.send("Tym razem udało się odesłać Dagona...")
            await voice_client.disconnect(force=True)

    @commands.command(
        name="play",
        brief="Ubłagaj przedwiecznego do odegrania pieśni z Youtube.",
        description='Uzyj linku do konkretnego utworu bądź podaj frazę po której Dagon wyszuka utworu na YT.',
    )
    async def _play(self, ctx, *, query: str = ""):
        if not query:
            return await ctx.send("Podaj link lub frazę jeżeli nie chcesz rozsłościć Dagona...")
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command("join"))
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            return  # TODO: play new song
        try:
            tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(query)
            player: wavelink.Player = ctx.voice_client
            player.autoplay = True
            print(f"Pobrane utwory: {tracks}")
            await player.play(tracks[0])
            await asyncio.sleep(1)
            await ctx.send(f"Dagon zagra Wam: **{player.current.title}** *({int(player.current.duration // 1000 // 60)}:{int(player.current.duration // 1000 % 60):02})*")
        except Exception as e:
            await ctx.send(f"Niech to Cthulhu kopnie, coś nie współpracuje : \n{e}")
            raise e

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

    @commands.hybrid_command(name="stop", brief="Poproś Dagona aby skończył już grać (ryzykowne).")
    async def _stop(self, ctx):
        player: wavelink.Player = ctx.guild.voice_client
        if player and player.is_playing():
            await player.stop(force=True)
            await ctx.send("Tym razem Dagon posłuchał i przestał grać.")
        else:
            await ctx.send("Czujesz na sobie mrożący wzrok Dagona - on nic obecnie nie gra.")

    @commands.command(brief="Poproś o krótką przerwę.")
    async def pause(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Dagon zgodził się przerwac na chwilę.")
        else:
            await ctx.send("Dagon spojrzał na Ciebie zdegustowany. Przecież obecnie nic nie śpiewa.")

    @commands.command(brief="Resume the paused song.")
    async def resume(self, ctx: Context):
        voice_client = ctx.voice_client

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Dagon wznawia swój śpiew.")
        else:
            await ctx.send("Czujesz na sobie wwieracjące się spojrzenie Dagona - przecież nie ma czego wznawiać.")

    @_play.before_invoke
    @_connect.before_invoke
    async def ensure_voice(self, ctx: Context):
        if not ctx.author.voice:
            await ctx.send("Musisz znajdować się w kręgu przywołań (kanale głosowym)")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot: commands.Bot):
    await bot.add_cog(Music(bot))
