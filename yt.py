import asyncio

import discord
import yt_dlp as youtube_dl

from config import ffmpeg_options, ytdl_format_options
from dataclasses import dataclass


@dataclass
class YoutubeAudio:
    title: str
    url: str
    original_url: str
    data: dict


def from_dict(data: dict) -> YoutubeAudio:
    return YoutubeAudio(
        title=data.get("title", ""),
        url=data.get("url", ""),
        original_url=data.get("original_url", ""),
        data=data
    )

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
        entries_data = data["entries"] if "entries" in data else [data]
        entries = convert_to_dataclass_list(entries_data)
        return entries

    @classmethod
    async def from_url(cls, audio: YoutubeAudio):
        audio_url = audio.url
        return cls(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), data=audio.data)


def convert_to_dataclass_list(entries_data):
    return [from_dict(entry) for entry in entries_data]
