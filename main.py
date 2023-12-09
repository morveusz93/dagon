import discord
from discord.ext import commands
import yt_dlp as youtube_dl


TOKEN = "MTE4MjczOTQ3MTAzMzE3MjA4MQ.GWelbj.Yln1aGKQ2dSvEUXx61qfgcU3H7oKak7Ia-VSR4"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user.name}")


@bot.command()
async def join(ctx):
    author_voice_channel = ctx.author.voice
    if author_voice_channel and author_voice_channel.channel:
        channel = author_voice_channel.channel
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client:
            await voice_client.disconnect()
        await channel.connect()
        await ctx.send(f"Bot dołączył do kanału głosowego: {channel.name}")
    else:
        await ctx.send("Musisz być na kanale głosowym, aby używać tego bota.")


@bot.command()
async def leave(ctx):
    voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_channel and voice_channel.is_connected():
        await voice_channel.disconnect()


@bot.command()
async def play(ctx, url=None):
    if not url:
        return await ctx.send('Musisz podac link do YT: "!play <link>"')
    voice_channel = ctx.author.voice.channel

    if not voice_channel:
        return await ctx.send("Musisz być na kanale głosowym, aby używać tego bota.")

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client or not voice_client.is_connected():
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            print(f"Wystąpił błąd: {e}")
            return await ctx.send(
                "Wystąpił błąd podczas dołączania do kanału głosowego."
            )

    elif voice_client.channel != voice_channel:
        return await ctx.send("Bot już jest na innym kanale głosowym.")

    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError:
            return await ctx.send("Wystąpił błąd. Upewnij się, że link jest poprawny.")
        formats = [
            x for x in info["formats"] if x["resolution"].lower() == "audio only"
        ]
        defaults = [d for d in formats if "medium" in d["format"]]
        if not defaults:
            defaults = [d for d in formats if d.get("format_note") == "Default"]
        if not defaults:
            defaults = formats
        try:
            music_url = defaults[0].get("url")
        except KeyError:
            ctx.send("Wystąpił błąd podczas pobrania muzyki z filmu, podaj inny link.")
        voice_client.play(
            discord.FFmpegPCMAudio(music_url),
            after=lambda e: print("Odtwarzanie zakończone"),
        )

    await ctx.send("Odtwarzam muzykę!")


bot.run(TOKEN)
