import os
from dotenv import load_dotenv

load_dotenv()


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVA_URL = os.getenv('LAVA_URL')
LAVA_PASSWORD = os.getenv('LAVA_PASSWORD')
SPOTIFY_USER = os.getenv('SPOTIFY_USER')
SPOTIFY_PASSWORD = os.getenv('SPOTIFY_PASSWORD')
