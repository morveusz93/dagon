import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify

from config import LAVA_URL, LAVA_PASSWORD, SPOTIFY_USER, SPOTIFY_PASSWORD


class Dagon(commands.Bot):
    def __init__(self):
        command_prefix = "!!"

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix), intents=intents
        )

        self.vol = 50

    async def on_ready(self):
        sc = spotify.SpotifyClient(
            client_id=SPOTIFY_USER,
            client_secret=SPOTIFY_PASSWORD
        )
        node: wavelink.Node = wavelink.Node(uri=LAVA_URL, password=LAVA_PASSWORD)
        await wavelink.NodePool.connect(client=self, nodes=[node], spotify=sc)
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Lavalink connected!")
        print("------")

    async def on_voice_state_update(self, member, before, after):
        voice_client = discord.utils.get(self.voice_clients, guild=member.guild)
        if voice_client and len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
