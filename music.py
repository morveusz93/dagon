import functools
from typing import Dict
import asyncio

import discord
from discord.ext import commands
import yt_dlp as youtube_dl

from playlist import Playlist



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists: Dict[int, Playlist] = {}

    async def check_play(self, ctx: commands.Context):
        client = ctx.voice_client
        while client and client.is_playing():
            await asyncio.sleep(1)

        self.bot.dispatch("track_end", ctx)

    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str):
        if ctx.voice_client is None:
            voice_channel = ctx.author.voice.channel
            if ctx.author.voice is None:
                await ctx.send("`You are not in a voice channel!`")
            if (ctx.author.voice):
                await voice_channel.connect()
        else: 
            pass
        FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
        YDL_OPTIONS = {'format':'bestaudio', 'default_search':'auto'}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'entries' in info:
                url2 = info['entries'][0]['formats'][0]['url']
                title = info['entries'][0]['title']
            elif 'formats' in  info:
                url2 = info['formats'][0]['url']
                title = info['title']
            
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            self.bot.dispatch("play_command", ctx, source, title)
        

    @commands.Cog.listener()
    async def on_play_command(self, ctx: commands.Context, song, title: str):
        playlist = self.playlists.get(ctx.guild.id, Playlist(ctx.guild.id))
        self.playlists[ctx.guild.id] = playlist
        to_add = (song, title)
        playlist.add_song(to_add)
        await ctx.send(f"`Added {title} to the playlist.`")
        if not ctx.voice_client.is_playing():
            self.bot.dispatch("track_end", ctx)

    @commands.Cog.listener()
    async def on_track_end(self, ctx: commands.Context):
        playlist = self.playlists.get(ctx.guild.id)
        if playlist and not playlist.is_empty:
            song, title = playlist.get_song()
        else:
            await ctx.send("No more songs in the playlist")
            return await ctx.guild.voice_client.disconnect()
        await ctx.send(f"Now playing: {title}")
        
        ctx.guild.voice_client.play(song, after=functools.partial(lambda x: self.bot.loop.create_task(self.check_play(ctx))))

async def setup(bot):
    await bot.add_cog(Music(bot))
