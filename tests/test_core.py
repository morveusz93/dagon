from unittest.mock import MagicMock

import pytest
from discord.ext import commands

import style
from cogs.core import GENERIC_ERROR, Core, help_embed
from cogs.fun import Fun
from cogs.mayo import Mayo
from cogs.rpg import Rpg
from errors import DagonError


@pytest.fixture
def bot():
    bot = MagicMock(text_prefix="!!")
    cogs = [Rpg(bot), Fun(bot), Mayo(bot), Core(bot)]
    bot.cogs = {c.qualified_name: c for c in cogs}
    return bot


def test_help_lists_every_command(bot):
    embed = help_embed(bot)
    text = "\n".join(f.value for f in embed.fields)
    for name in ["roll", "motivate", "cat", "dog", "duck", "fox", "majonez", "help"]:
        assert f"`/{name}" in text
    assert "`/roll <rzut>`" in text
    assert "`!!m`" in text
    assert [f.name for f in embed.fields] == [
        "🎲 Kości",
        "🖼️ Malowidła",
        "🥚 Majonez",
        "ℹ️ Inne",
    ]


def test_all_slash_descriptions_fit_discord_limit(bot):
    for cog in bot.cogs.values():
        for cmd in cog.get_commands():
            assert 1 <= len(cmd.description) <= 100, cmd.name
            for param in cmd.app_command.parameters:
                assert 1 <= len(param.description) <= 100, (cmd.name, param.name)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error, expected",
    [
        (commands.CommandInvokeError(DagonError("buu")), "buu"),
        (commands.HybridCommandError(DagonError("buu")), "buu"),
        (commands.CommandInvokeError(RuntimeError("x")), GENERIC_ERROR),
    ],
)
async def test_errors_are_shown_as_error_embed(bot, ctx, error, expected):
    await Core(bot).on_command_error(ctx, error)

    embed = ctx.send.call_args.kwargs["embed"]
    assert embed.color == style.ERROR_COLOR
    assert embed.description == expected
    assert ctx.send.call_args.kwargs["ephemeral"] is True


@pytest.mark.asyncio
async def test_unknown_command_is_ignored(bot, ctx):
    await Core(bot).on_command_error(ctx, commands.CommandNotFound())
    ctx.send.assert_not_awaited()
