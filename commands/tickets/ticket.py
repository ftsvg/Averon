from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Role, Thread

from core import LOGO, check_ticket_config_permissions
from ui import normal, error, log_embed
from ui.views import TicketsView
from content import COMMANDS, COMMAND_ERRORS
from database.handlers import TicketSettingsManager, TicketManager
from database import Ticket, TicketSettings


class Tickets(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    ticket = app_commands.Group(
        name='ticket',
        description='Ticket related commands.',
    )

    @ticket.command(
        name=COMMANDS['ticket_channel']['name'],
        description=COMMANDS['ticket_channel']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['ticket_channel']['channel']
    )
    async def ticket_channel(
        self, 
        interaction: Interaction,
        channel: TextChannel
    ):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "config"):
            return

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_ticket_channel(channel.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Ticket channel", author_icon_url=LOGO,
                description=f"Ticket channel set to {channel.mention}"
            )
        )


    @ticket.command(
        name=COMMANDS['ticket_role']['name'],
        description=COMMANDS['ticket_role']['description']
    )
    @app_commands.describe(
        role=COMMANDS['ticket_role']['role']
    )
    async def ticket_role(
        self, 
        interaction: Interaction,
        role: Role
    ):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "config"):
            return

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_staff_role(role.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Ticket staff role", author_icon_url=LOGO,
                description=f"Ticket staff role set to {role.mention}"
            )
        )


    @ticket.command(
        name=COMMANDS['ticket_transcripts']['name'],
        description=COMMANDS['ticket_transcripts']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['ticket_transcripts']['channel']
    )
    async def ticket_transcripts(
        self, 
        interaction: Interaction,
        channel: TextChannel
    ):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "config"):
            return

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_transcripts_channel(channel.id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Ticket transcripts", author_icon_url=LOGO,
                description=f"Ticket transcripts channel set to {channel.mention}"
            )
        )


    @ticket.command(
        name=COMMANDS['ticket_panel']['name'],
        description=COMMANDS['ticket_panel']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['ticket_panel']['channel']
    )
    async def ticket_panel(
        self, 
        interaction: Interaction,
        channel: TextChannel
    ):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "config"):
            return

        embed = normal(
            author_name="Support Tickets", author_icon_url=LOGO,
            description="Click on the button below to create a ticket."
        )

        await channel.send(
            embed=embed,
            view=TicketsView(self.client)
        )

        await interaction.edit_original_response(
            embed=normal(
                author_name="Ticket panel", author_icon_url=LOGO,
                description=f"Successfully sent the ticket panel to {channel.mention}"
            )
        )


    @ticket.command(
        name=COMMANDS['ticket_close']['name'],
        description=COMMANDS['ticket_close']['description']
    )
    @app_commands.describe(
        channel=COMMANDS['ticket_close']['channel']
    )
    async def ticket_close(
        self, 
        interaction: Interaction,
        channel: Thread
    ):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "other"):
            return
        
        manager = TicketManager(interaction.guild.id)

        ticket = manager.get_ticket(channel.id)
        if not ticket:
            return await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS['ticket_not_found_error']['title'],
                    description=COMMAND_ERRORS['ticket_not_found_error']['message']
                )
        )

        manager.close_ticket(
            channel_id=channel.id,
            closed_by=interaction.user.id
        )
        
        await interaction.edit_original_response(
            embed=normal(
                author_name="Ticket closed", author_icon_url=LOGO,
                description="The ticket has been closed and deleted."
            )
        )

        ticket_details: Ticket = manager.get_ticket(interaction.channel.id)
        user = interaction.guild.get_member(ticket_details.user_id)

        settings: TicketSettings = TicketSettingsManager(interaction.guild.id).get_settings()
        transcript_channel = interaction.guild.get_channel(settings.transcripts_channel_id)

        embed = log_embed(
            author_name="Transcript",
            fields=[
                ("ticket", f"{interaction.channel.name} `{interaction.channel.id}`", False),
                ("ticket reason", ticket_details.reason, False),
                ("created at", f"<t:{ticket_details.created_at}:R>", False),
                ("user", f"{user.name} `{user.id}`", False),
                ("closed by", f"{interaction.user.name} `{interaction.user.id}`", False)
            ],
            thumbnail=user.display_avatar.url if user.display_avatar.url else None
        )

        if transcript_channel:
            await transcript_channel.send(embed=embed)        

        await channel.delete(
            reason=f"Ticket closed by {interaction.user}"
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Tickets(client))