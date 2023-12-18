import discord
from discord.ext import commands


class Dagon(commands.Bot):
    def __init__(self):
        command_prefix = "!d"

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix),
            intents=intents
        )

        self.vol = 50

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
