from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from cogs.mayo import REACTION, Mayo, mentions_winiary


@pytest.mark.parametrize(
    "text",
    ["Winiary", "Winiary to najlepszy majonez", "WINIARY!!!", "a może (Winiary)?"],
)
def test_detects_winiary(text):
    assert mentions_winiary(text)


@pytest.mark.parametrize(
    "text",
    [
        "winiary",
        "WiNiArY",
        "nie ma lepszego od winiarów",
        "w Winiarach",
        "Winiarski",
        "znajomy winiarz",
        "kielecki rządzi",
        "",
    ],
)
def test_ignores_other_words(text):
    assert not mentions_winiary(text)


def make_message(content, *, bot=False):
    message = MagicMock()
    message.content = content
    message.author.bot = bot
    message.add_reaction = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_reacts_to_winiary():
    message = make_message("Winiary są najlepsze")
    await Mayo(MagicMock()).on_message(message)
    message.add_reaction.assert_awaited_once_with(REACTION)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message", [make_message("kielecki"), make_message("Winiary", bot=True)]
)
async def test_does_not_react(message):
    await Mayo(MagicMock()).on_message(message)
    message.add_reaction.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_permission_does_not_crash():
    message = make_message("WINIARY")
    message.add_reaction.side_effect = discord.Forbidden(MagicMock(status=403), "no")
    await Mayo(MagicMock()).on_message(message)
