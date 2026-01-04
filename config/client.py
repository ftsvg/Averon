import os
from discord.ext import commands
from discord import app_commands, Intents, Interaction

from logger import logger
from core import InteractionErrorHandler


intents = Intents.all()
intents.message_content = True


class Client(commands.AutoShardedBot):
    def __init__(
        self, *, intents: Intents = intents
    ):
        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('!')
        )


    async def setup_hook(self):
        for folder in os.listdir("commands"):
            for cog in os.listdir(f"commands/{folder}"):
                if cog.endswith(".py"):
                    try:
                        await self.load_extension(name=f"commands.{folder}.{cog[:-3]}")
                        logger.info(f"Loaded: {cog[:-3]} cog")

                    except commands.errors.ExtensionNotFound:
                        logger.warning(f"Failed to load {cog[:-3]}")
        
        self.tree.on_error = self.on_app_command_error


    async def on_app_command_error(
        self,
        interaction: Interaction,
        error: app_commands.AppCommandError
    ):
        await InteractionErrorHandler.handle(interaction, error)


    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')