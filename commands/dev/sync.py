import traceback

from discord.ext import commands

from ui import create_embed
from database.handlers import LoggingManager


class Sync(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):

        try:
            await self.client.tree.sync()
            embed = create_embed(
                author_name="Synced",
                description="Successfully synced slash commands."
            )
            await ctx.reply(embed=embed)
        
        except Exception:
            LoggingManager(ctx.guild.id).create_log('ERROR', traceback.format_exc())



async def setup(client: commands.Bot) -> None:
    await client.add_cog(Sync(client))