import datetime as dt
from unittest.mock import MagicMock

import pytest

from cogs import mayo
from cogs.mayo import MAYONNAISES, Mayo, mayo_of_the_day


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
