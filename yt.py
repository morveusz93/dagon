import asyncio

import discord
import yt_dlp as youtube_dl

from config import ffmpeg_options, ytdl_format_options

youtube_dl.utils.bug_reports_message = lambda: ""
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def get_audio_entries(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        return data["entries"] if "entries" in data else [data]

    @classmethod
    async def from_url(cls, data):
        audio_url = data["url"]
        return cls(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), data=data)
