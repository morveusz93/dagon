import logging

import discord
from discord.ext import commands

import style
from errors import DagonError, unwrap

log = logging.getLogger(__name__)

GENERIC_ERROR = "Coś zgrzytnęło w głębinach. Spróbuj ponownie za chwilę."


class Core(commands.Cog, description="ℹ️ Inne"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Pokaż, co potrafi Dagon.")
    async def help(self, ctx: commands.Context):
        await ctx.send(
            embed=help_embed(self.bot, ctx.guild.id if ctx.guild else None),
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        err = unwrap(error)
        if isinstance(err, commands.CommandNotFound):
            return
        if isinstance(err, DagonError):
            message = str(err)
        elif isinstance(err, commands.UserInputError):
            message = f"Dagon nie rozumie. Użycie: `{usage(ctx.command)}`"
        else:
            log.error("Command %s failed", ctx.command, exc_info=err)
            message = GENERIC_ERROR
        await ctx.send(embed=style.error_embed(message), ephemeral=True)


def usage(command: commands.Command) -> str:
    return f"/{command.name} {command.signature}".strip()


def help_embed(bot, guild_id: int | None = None) -> discord.Embed:
    prefix = getattr(bot, "text_prefix", "!!")
    embed = style.embed(
        f"Wpisz `/` i wybierz komendę albo użyj prefiksu `{prefix}`, "
        f"np. `{prefix}roll 3d6`.",
        title="📜 Księga Dagona",
    )
    for cog in bot.cogs.values():
        lines = []
        for cmd in cog.get_commands():
            if cmd.hidden:
                continue
            line = f"`{usage(cmd)}` — {cmd.description}"
            if cmd.aliases:
                line += " (" + ", ".join(f"`{prefix}{a}`" for a in cmd.aliases) + ")"
            lines.append(line)
        # Slash-only commands that exist on some servers only (e.g. /postac cthulhu).
        extra = getattr(cog, "help_lines", None)
        if callable(extra):
            lines += extra(guild_id)
        if lines:
            embed.add_field(
                name=cog.description or cog.qualified_name,
                value="\n".join(lines),
                inline=False,
            )
    return embed


async def setup(bot):
    await bot.add_cog(Core(bot))
