from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest

from cogs.core import help_embed
from cogs.postac import LINK_TTL_SECONDS, Postac, link_url, make_link_token
from cogs.rpg import Rpg
from config import CocConfig, coc_config

SECRET = "s" * 32
CONFIG = CocConfig(app_url="https://coc.example", link_secret=SECRET, guild_id=111)


def decode(token: str, **kwargs):
    return jwt.decode(
        token, SECRET, algorithms=["HS256"], audience="coc-link", **kwargs
    )


def test_token_carries_who_and_where_for_15_minutes():
    token = make_link_token(
        CONFIG, user_id=333, name="Mateusz", guild_id=111, channel_id=222, now=1_000_000
    )
    claims = decode(token, options={"verify_exp": False})
    assert claims["sub"] == "333"
    assert claims["name"] == "Mateusz"
    assert claims["system"] == "coc7"
    assert (claims["guild_id"], claims["channel_id"]) == ("111", "222")
    assert claims["exp"] - claims["iat"] == LINK_TTL_SECONDS == 15 * 60
    assert len(claims["jti"]) == 32


def test_every_link_is_different():
    a = make_link_token(
        CONFIG, user_id=1, name="a", guild_id=111, channel_id=2, now=1_000_000
    )
    b = make_link_token(
        CONFIG, user_id=1, name="a", guild_id=111, channel_id=2, now=1_000_000
    )
    assert a != b


def test_expired_and_forged_tokens_do_not_verify():
    old = make_link_token(
        CONFIG, user_id=1, name="a", guild_id=111, channel_id=2, now=1_000_000
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode(old)
    other = CocConfig(app_url=CONFIG.app_url, link_secret="x" * 32, guild_id=111)
    with pytest.raises(jwt.InvalidSignatureError):
        decode(make_link_token(other, user_id=1, name="a", guild_id=111, channel_id=2))


def test_long_display_names_are_cut():
    token = make_link_token(
        CONFIG, user_id=1, name="x" * 200, guild_id=111, channel_id=2
    )
    assert len(decode(token)["name"]) == 64


def test_link_url():
    assert link_url(CONFIG, "abc") == "https://coc.example/start?t=abc"


@pytest.mark.parametrize(
    "env, ok",
    [
        (
            {
                "COC_APP_URL": "https://coc.example/",
                "COC_LINK_SECRET": SECRET,
                "COC_GUILD_ID": "111",
            },
            True,
        ),
        (
            {
                "COC_APP_URL": "http://localhost:3000",
                "COC_LINK_SECRET": SECRET,
                "COC_GUILD_ID": "111",
            },
            True,
        ),
        (
            {
                "COC_APP_URL": "http://coc.example",
                "COC_LINK_SECRET": SECRET,
                "COC_GUILD_ID": "111",
            },
            False,
        ),
        (
            {
                "COC_APP_URL": "https://coc.example",
                "COC_LINK_SECRET": "short",
                "COC_GUILD_ID": "111",
            },
            False,
        ),
        (
            {
                "COC_APP_URL": "https://coc.example",
                "COC_LINK_SECRET": SECRET,
                "COC_GUILD_ID": "abc",
            },
            False,
        ),
        ({}, False),
    ],
)
def test_coc_config(env, ok):
    config = coc_config(env)
    assert (config is not None) == ok
    if ok:
        assert not config.app_url.endswith("/")


def interaction(guild_id: int):
    i = MagicMock()
    i.guild_id = guild_id
    i.channel_id = 222
    i.user.id = 333
    i.user.display_name = "Mateusz"
    i.response.send_message = AsyncMock()
    return i


@pytest.mark.asyncio
async def test_command_replies_privately_with_a_link_button():
    cog = Postac(MagicMock(), CONFIG)
    i = interaction(111)
    await cog.cthulhu.callback(cog, i)
    kwargs = i.response.send_message.call_args.kwargs
    assert kwargs["ephemeral"] is True
    button = kwargs["view"].children[0]
    assert button.url.startswith("https://coc.example/start?t=")
    token = button.url.split("t=", 1)[1]
    assert decode(token)["channel_id"] == "222"


@pytest.mark.asyncio
async def test_command_refuses_other_servers():
    cog = Postac(MagicMock(), CONFIG)
    i = interaction(999)
    await cog.cthulhu.callback(cog, i)
    kwargs = i.response.send_message.call_args.kwargs
    assert kwargs["ephemeral"] is True
    assert "view" not in kwargs


def test_help_shows_postac_only_on_the_party_server():
    bot = MagicMock(text_prefix="!!")
    cogs = [Rpg(bot), Postac(bot, CONFIG)]
    bot.cogs = {c.qualified_name: c for c in cogs}
    on_party = "\n".join(f.value for f in help_embed(bot, 111).fields)
    elsewhere = "\n".join(f.value for f in help_embed(bot, 999).fields)
    assert "/postac cthulhu" in on_party
    assert "/postac" not in elsewhere
