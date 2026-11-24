"""Wspólny wygląd odpowiedzi Dagona."""

import discord

COLOR = discord.Color(0x1F6F78)  # głębiny
ERROR_COLOR = discord.Color(0x8B1E3F)


def embed(description: str | None = None, *, title: str | None = None) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=COLOR)


def error_embed(description: str) -> discord.Embed:
    return discord.Embed(
        title="🐙 Dagon marszczy macki",
        description=description,
        color=ERROR_COLOR,
    )
