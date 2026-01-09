from discord.ext import commands
from discord import app_commands, Interaction, TextChannel, Role, Thread

from core import check_permissions, send_transcript_log, send_user_dm
from ui import create_embed
from ui.views import TicketsView
from content import COMMANDS, ERRORS, DESCRIPTIONS
from database.handlers import (
    TicketSettingsManager,
    TicketManager,
    LoggingManager
)
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
    @app_commands.describe(channel=COMMANDS['ticket_channel']['channel'])
    async def ticket_channel(
        self,
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        1/0

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "admin"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to set "
                f"ticket channel to {channel} ({channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_ticket_channel(channel.id)

        logging_manager.create_log(
            'INFO',
            f"Ticket channel updated: {interaction.user} ({interaction.user.id}) set "
            f"ticket channel to {channel} ({channel.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['ticket_channel_set'].format(channel.mention)
        )


    @ticket.command(
        name=COMMANDS['ticket_role']['name'],
        description=COMMANDS['ticket_role']['description']
    )
    @app_commands.describe(role=COMMANDS['ticket_role']['role'])
    async def ticket_role(
        self,
        interaction: Interaction,
        role: Role
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "admin"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to set "
                f"ticket staff role to {role} ({role.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_staff_role(role.id)

        logging_manager.create_log(
            'INFO',
            f"Ticket staff role updated: {interaction.user} ({interaction.user.id}) set "
            f"staff role to {role} ({role.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['ticket_staff_role_set'].format(role.name)
        )


    @ticket.command(
        name=COMMANDS['ticket_transcripts']['name'],
        description=COMMANDS['ticket_transcripts']['description']
    )
    @app_commands.describe(channel=COMMANDS['ticket_transcripts']['channel'])
    async def ticket_transcripts(
        self,
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "admin"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to set "
                f"ticket transcript channel to {channel} ({channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        settings = TicketSettingsManager(interaction.guild.id)
        settings.set_transcripts_channel(channel.id)

        logging_manager.create_log(
            'INFO',
            f"Ticket transcript channel updated: {interaction.user} ({interaction.user.id}) set "
            f"transcript channel to {channel} ({channel.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['ticket_transcript_channel_set'].format(channel.mention)
        )


    @ticket.command(
        name=COMMANDS['ticket_panel']['name'],
        description=COMMANDS['ticket_panel']['description']
    )
    @app_commands.describe(channel=COMMANDS['ticket_panel']['channel'])
    async def ticket_panel(
        self,
        interaction: Interaction,
        channel: TextChannel
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "admin"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to send "
                f"ticket panel to {channel} ({channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        await channel.send(
            embed=create_embed(
                author_name="Support Tickets",
                description="Click on the button below to create a ticket."
            ),
            view=TicketsView(self.client)
        )

        logging_manager.create_log(
            'INFO',
            f"Ticket panel sent: {interaction.user} ({interaction.user.id}) sent "
            f"ticket panel to {channel} ({channel.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['ticket_panel_sent'].format(channel.mention)
        )


    @ticket.command(
        name=COMMANDS['ticket_close']['name'],
        description=COMMANDS['ticket_close']['description']
    )
    @app_commands.describe(channel=COMMANDS['ticket_close']['channel'])
    async def ticket_close(
        self,
        interaction: Interaction,
        channel: Thread
    ):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "other"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to close "
                f"ticket thread {channel} ({channel.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        manager = TicketManager(interaction.guild.id)
        ticket = manager.get_ticket(channel.id)

        if not ticket:
            logging_manager.create_log(
                'INFO',
                f"Ticket close failed: Ticket for channel {channel.id} does not exist "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.edit_original_response(
                content=ERRORS['ticket_not_found_error']
            )

        manager.close_ticket(
            channel_id=channel.id,
            closed_by=interaction.user.id
        )

        logging_manager.create_log(
            'INFO',
            f"Ticket closed: Ticket {channel.id} closed by "
            f"{interaction.user} ({interaction.user.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['ticket_closed'].format(channel.mention)
        )

        ticket_details: Ticket = manager.get_ticket(channel.id)
        user = interaction.guild.get_member(ticket_details.user_id)

        embed = create_embed(
            author_name="Transcript",
            fields=[
                ("Ticket", f"{channel.name} `{channel.id}`", False),
                ("Reason", ticket_details.reason, False),
                ("Created At", f"<t:{ticket_details.created_at}:R>", False),
                ("User", f"{user.name} `{user.id}`", False),
                ("Closed By", f"{interaction.user.name} `{interaction.user.id}`", False)
            ],
            thumbnail=user.display_avatar.url if user and user.display_avatar else None
        )

        await send_transcript_log(interaction, embed)
        await send_user_dm(interaction, user, embed=embed)

        await channel.delete()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Tickets(client))