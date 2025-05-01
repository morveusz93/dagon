import os
from dotenv import load_dotenv

load_dotenv()

required_env_vars = [
    'DISCORD_TOKEN',
    'LAVA_URL',
    'LAVA_PASSWORD',
]

missing = [var for var in required_env_vars if os.getenv(var) is None]

if missing:
    raise RuntimeError(f'Missing required environment variables: {", ".join(missing)}')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LAVA_URL = os.getenv('LAVA_URL')
LAVA_PASSWORD = os.getenv('LAVA_PASSWORD')
SPOTIFY_USER = os.getenv('SPOTIFY_USER')
SPOTIFY_PASSWORD = os.getenv('SPOTIFY_PASSWORD')
