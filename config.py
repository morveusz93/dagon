import os

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVA_URL = os.getenv('LAVA_URL')
LAVA_PASSWORD = os.getenv('LAVA_PASSWORD')
SPOTIFY_USER = os.getenv('SPOTIFY_USER')
SPOTIFY_PASSWORD = os.getenv('SPOTIFY_PASSWORD')
