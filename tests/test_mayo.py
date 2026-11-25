import datetime as dt
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from cogs import mayo
from cogs.mayo import MAYONNAISES, REACTION, Mayo, mayo_of_the_day, mentions_winiary


@pytest.mark.parametrize(
    "text",
    [
        "Winiary",
        "winiary",
        "WiNiArY",
        "wINIARY",
        "Winiary to najlepszy majonez",
        "WINIARY!!!",
        "a może (winiary)?",
    ],
)
def test_detects_winiary(text):
    assert mentions_winiary(text)


@pytest.mark.parametrize(
    "text",
    [
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


def test_mayo_of_the_day_is_stable_within_a_day():
    day = dt.date(2026, 11, 24)
    assert mayo_of_the_day(day, 123) == mayo_of_the_day(day, 123)


def test_mayo_of_the_day_returns_known_mayo_and_its_verdict():
    for offset in range(60):
        name, verdict = mayo_of_the_day(dt.date(2026, 1, 1) + dt.timedelta(offset), 1)
        assert verdict in MAYONNAISES[name]


def test_every_mayo_can_win():
    winners = {
        mayo_of_the_day(dt.date(2026, 1, 1) + dt.timedelta(d), 1)[0] for d in range(365)
    }
    assert winners == set(MAYONNAISES)


def test_mayo_changes_between_days_and_servers():
    day = dt.date(2026, 1, 1)
    by_day = {mayo_of_the_day(day + dt.timedelta(d), 1) for d in range(30)}
    by_guild = {mayo_of_the_day(day, g) for g in range(30)}
    assert len(by_day) > 1 and len(by_guild) > 1


@pytest.mark.asyncio
async def test_majonez_command_sends_embed(ctx, monkeypatch):
    monkeypatch.setattr(mayo, "today", lambda: dt.date(2026, 11, 24))
    ctx.guild.id = 42
    cog = Mayo(MagicMock())

    await cog.majonez.callback(cog, ctx)

    embed = ctx.send.call_args.kwargs["embed"]
    name, verdict = mayo_of_the_day(dt.date(2026, 11, 24), 42)
    assert f"**{name}**" in embed.description and verdict in embed.description
    assert embed.footer.text == "24.11.2026"
