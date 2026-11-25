"""/postac cthulhu: a personal, 15-minute sign-in link to the private CoC creator.

The link carries a JWT signed with COC_LINK_SECRET (shared with coc-creator,
which verifies it at /start). Slash-only and ephemeral: a prefix version
would post the link where everyone can see it.
"""

import time
import uuid

import discord
import jwt
from discord import app_commands
from discord.ext import commands

import style
from config import COC, CocConfig

LINK_TTL_SECONDS = 15 * 60
LINK_AUDIENCE = "coc-link"
LINK_SYSTEM = "coc7"


def make_link_token(
    config: CocConfig,
    *,
    user_id: int,
    name: str,
    guild_id: int,
    channel_id: int,
    now: float | None = None,
) -> str:
    issued = int(time.time() if now is None else now)
    return jwt.encode(
        {
            "sub": str(user_id),
            "name": name[:64],
            "system": LINK_SYSTEM,
            "aud": LINK_AUDIENCE,
            "iat": issued,
            "exp": issued + LINK_TTL_SECONDS,
            "jti": uuid.uuid4().hex,
            "guild_id": str(guild_id),
            "channel_id": str(channel_id),
        },
        config.link_secret,
        algorithm="HS256",
    )


def link_url(config: CocConfig, token: str) -> str:
    return f"{config.app_url}/start?t={token}"


def link_reply(url: str) -> tuple[discord.Embed, discord.ui.View]:
    embed = style.embed(
        "Twój osobisty link do kreatora badacza. Działa **15 minut** i widzisz go "
        "tylko ty: nie przekazuj go dalej.\n\n"
        "Po wejściu zostajesz zalogowany na 30 dni, więc postać możesz tworzyć "
        "spokojnie, na raty.",
        title="🐙 Kreator badacza",
    )
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Otwórz kreator", emoji="📜", url=url))
    return embed, view


class Postac(commands.Cog, description="🐙 Postacie"):
    postac = app_commands.Group(
        name="postac", description="Kreatory postaci", guild_only=True
    )

    def __init__(self, bot, config: CocConfig):
        self.bot = bot
        self.config = config

    @postac.command(
        name="cthulhu",
        description="Osobisty link do kreatora badacza Call of Cthulhu (15 min).",
    )
    async def cthulhu(self, interaction: discord.Interaction):
        if interaction.guild_id != self.config.guild_id:
            await interaction.response.send_message(
                embed=style.error_embed("Ta komenda działa tylko na serwerze drużyny."),
                ephemeral=True,
            )
            return
        token = make_link_token(
            self.config,
            user_id=interaction.user.id,
            name=interaction.user.display_name,
            guild_id=interaction.guild_id,
            channel_id=interaction.channel_id,
        )
        embed, view = link_reply(link_url(self.config, token))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def help_lines(self, guild_id: int | None) -> list[str]:
        """Shown in /help only on the server where the command exists."""
        if guild_id != self.config.guild_id:
            return []
        return [
            "`/postac cthulhu` — Osobisty link do kreatora badacza (15 min, widzisz go tylko ty)."
        ]


async def setup(bot):
    if COC is None:
        return
    await bot.add_cog(Postac(bot, COC), guild=discord.Object(id=COC.guild_id))
