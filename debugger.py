import yt_dlp as youtube_dl
from config import ydl_opts
from utils import get_playback_url

url = "https://www.youtube.com/watch?v=v4pi1LxuDHc&list=RDMMv4pi1LxuDHc&start_radio=1"

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    if "entries" in info:
        playlist_url = url
        print(info["entries"][:50])
        exit()
        for entry in info["entries"]:
            playback_url = get_playback_url(entry)
            print(playback_url)
    else:
        # one video
        playback_url = get_playback_url(info)
        print(playback_url)
