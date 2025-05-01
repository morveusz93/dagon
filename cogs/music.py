import asyncio
import time

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
        player: wavelink.Player = ctx.voice_client
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await player.stop(force=True)
        try:
            tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(query)
            if not tracks:
                return await ctx.send("Nie znaleziono podanego utwaoru, spróbuj z innym.")
            player.autoplay = True
            await player.play(tracks[0])
            await ctx.send(f"Dagon zagra Wam: **{player.current.title}** *({int(player.current.duration // 1000 // 60)}:{int(player.current.duration // 1000 % 60):02})*")
        except Exception as e:
            await ctx.send(f"Niech to Cthulhu kopnie, coś nie współpracuje : \n{e}")
            raise e

    @commands.command(brief="Ustaw głośność Dagona w przedziale 0-100.")
    async def vol(self, ctx, volume: int) -> None:
        if ctx.voice_client is None:
            return await ctx.send("Żeby to zrobić musisz być na kanale głosowym.")
        if volume > 100 or volume < 0:
            return await ctx.send("Podaj liczbę w przedziale 0-100.")
        curr_vol = ctx.voice_client.volume
        await ctx.voice_client.set_volume(volume)
        if curr_vol > volume:
            text = "Dagon postara się być ciszej."
        else:
            text = "Dagon będzie grać głośniej."
        await ctx.send(text)

    @commands.hybrid_command(name="stop", brief="Poproś Dagona aby skończył już grać (ryzykowne).")
    async def _stop(self, ctx):
        player: wavelink.Player = ctx.guild.voice_client
        if player and player.is_playing():
            await player.stop(force=True)
            await ctx.send("Tym razem Dagon posłuchał i przestał grać.")
        else:
            await ctx.send("Czujesz na sobie mrożący wzrok Dagona - on nic obecnie nie gra.")

    @commands.hybrid_command(name="pause", brief="Poproś Dagona o krótką przerwę.")
    async def _pause(self, ctx):
        player: wavelink.Player = ctx.guild.voice_client
        if player and player.is_playing():
            await player.pause()
            await ctx.send("Dagon zrobi sobie krótką przerwę.")
        else:
            return await ctx.send("Czujesz na sobie mrożący wzrok Dagona - on nic obecnie nie gra.")

    @commands.hybrid_command(name="resume", brief="Poproś Dagona o wznowienie.")
    async def _resume(self, ctx):
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return await ctx.send("Czujesz na sobie mrożący wzrok Dagona - on nic obecnie nie gra.")
        elif player.is_paused():
            await player.resume()
            await ctx.send(f"Dagon powraca do grania **{player.current.title}** *({int(player.current.duration // 1000 // 60)}:{int(player.current.duration // 1000 % 60):02})*.")
        else:
            return await ctx.send("Czujesz na sobie mrożący wzrok Dagona - on obecnie gra.")

    @_play.before_invoke
    @_connect.before_invoke
    async def ensure_voice(self, ctx: Context):
        if not ctx.author.voice:
            await ctx.send("Musisz znajdować się w kręgu przywołań (kanale głosowym)")
            raise commands.CommandError("Author not connected to a voice channel.")


async def setup_music(bot: commands.Bot):
    await bot.add_cog(Music(bot))
