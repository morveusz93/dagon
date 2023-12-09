import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
from config import ydl_opts
from utils import get_playback_url


TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!d", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if (
        voice_client
        and len(voice_client.channel.members) == 1
        and bot.user in voice_client.channel.members
    ):
        await voice_client.disconnect()


@bot.command()
async def join(ctx):
    author_voice_channel = ctx.author.voice
    if author_voice_channel and author_voice_channel.channel:
        channel = author_voice_channel.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client:
            await voice_client.disconnect()
        await channel.connect()
        await ctx.send(f"Dagon has been summoned to the voice channel: {channel.name}")
    else:
        await ctx.send("You must be in a voice channel to summon Dagon.")


@bot.command()
async def leave(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_connected():
        await voice_channel.disconnect()


@bot.command()
async def play(ctx, url=None):
    if not url:
        return await ctx.send('You must provide a YouTube link: "!play <link>"')

    author_voice_channel = ctx.author.voice.channel
    if not author_voice_channel:
        return await ctx.send("You must be in a voice channel to summon Dagon.")

    bot_voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not bot_voice_channel or not bot_voice_channel.is_connected():
        try:
            bot_voice_channel = await author_voice_channel.connect()
        except Exception as e:
            print(f"Error occurred: {e}")
            return await ctx.send("Error occurred while summoning Dagon to the voice channel.")

    elif bot_voice_channel.channel != author_voice_channel:
        return await ctx.send("Dagon is already summoned to another voice channel.")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError:
            return await ctx.send("Error occurred. Make sure the link is correct.")

        playback_url = get_playback_url(info)
        if not playback_url:
            return await ctx.send("Error occurred while fetching music from the video, please provide another link.")

        bot_voice_channel.play(
            discord.FFmpegPCMAudio(playback_url),
            after=lambda e: print("Playback finished"),
        )

    await ctx.send("Summoning Dagon to play music!")


bot.run(TOKEN)
