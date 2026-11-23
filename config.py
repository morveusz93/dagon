import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!!")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing required environment variable: DISCORD_TOKEN")
