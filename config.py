import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!!")

if not DISCORD_TOKEN:
    raise RuntimeError("Missing required environment variable: DISCORD_TOKEN")

# HS256 secrets shorter than this are refused (same rule as coc-creator).
MIN_SECRET_LENGTH = 32


@dataclass(frozen=True)
class CocConfig:
    """/postac cthulhu: link to the private Call of Cthulhu creator."""

    app_url: str
    link_secret: str
    guild_id: int


def coc_config(env) -> CocConfig | None:
    """All three COC_* variables set and valid, or None (the command is off)."""
    url = (env.get("COC_APP_URL") or "").strip().rstrip("/")
    secret = env.get("COC_LINK_SECRET") or ""
    guild = (env.get("COC_GUILD_ID") or "").strip()
    if not (url.startswith("https://") or url.startswith("http://localhost")):
        return None
    if len(secret) < MIN_SECRET_LENGTH or not guild.isdigit():
        return None
    return CocConfig(app_url=url, link_secret=secret, guild_id=int(guild))


COC = coc_config(os.environ)
