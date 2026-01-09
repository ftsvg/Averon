import asyncio
from discord import (
    Client,
    Interaction,
    ButtonStyle,
    TextStyle,
    ChannelType,
    AllowedMentions
)
from discord.ui import View, button, Button, Modal, TextInput

from database.handlers import (
    TicketManager,
    TicketSettingsManager,
    LoggingManager
)
from database import Ticket, TicketSettings
from ui import create_embed
from content import ERRORS, DESCRIPTIONS
from core import check_permissions


class TicketsView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Create ticket", style=ButtonStyle.gray, custom_id="create_ticket")
    async def create(self, interaction: Interaction, button: Button):
        logging_manager = LoggingManager(interaction.guild.id)

        manager = TicketManager(interaction.guild.id)
        ticket: Ticket = manager.get_ticket_by_user(interaction.user.id)

        if ticket:
            logging_manager.create_log(
                'INFO',
                f"Ticket creation blocked: {interaction.user} ({interaction.user.id}) "
                f"already has open ticket {ticket.channel_id}"
            )
            return await interaction.response.send_message(
                content=DESCRIPTIONS['ticket_already_open'].format(ticket.channel_id),
                ephemeral=True
            )

        await interaction.response.send_modal(TicketReasonView(self.client))


class TicketReasonView(Modal, title="Support ticket"):
    reason = TextInput(
        label="Ticket reason",
        placeholder="I need help with...",
        style=TextStyle.paragraph,
        required=True,
        min_length=3,
        max_length=512
    )

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild.id
        logging_manager = LoggingManager(guild_id)

        manager = TicketManager(guild_id)
        settings: TicketSettings = TicketSettingsManager(guild_id).get_settings()

        if (
            settings is None
            or settings.staff_role_id is None
            or settings.ticket_channel_id is None
            or settings.transcripts_channel_id is None
        ):
            logging_manager.create_log(
                'ERROR',
                f"Ticket creation failed: ticket system not configured "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.followup.send(
                content=ERRORS['ticket_config_not_set_error'],
                ephemeral=True
            )

        channel = interaction.guild.get_channel(settings.ticket_channel_id)
        staff_role = interaction.guild.get_role(settings.staff_role_id)

        thread = await channel.create_thread(
            name=f"ticket-{interaction.user.name}",
            type=ChannelType.private_thread,
            reason=self.reason.value
        )

        for member in staff_role.members:
            await thread.add_user(member)

        await thread.send(
            content=f"Welcome {interaction.user.mention}!",
            allowed_mentions=AllowedMentions(users=True),
            embed=create_embed(
                author_name="Support ticket",
                description=(
                    "A staff member will assist you shortly.\n"
                    "Please provide any additional details if needed."
                ),
                fields=[
                    ("User", f"{interaction.user.name} `{interaction.user.id}`", False),
                    ("Reason", self.reason.value, False)
                ],
                thumbnail=interaction.user.display_avatar.url if interaction.user.display_avatar else None
            ),
            view=CloseTicketView(self.client)
        )

        manager.create_ticket(
            interaction.user.id,
            thread.id,
            self.reason.value
        )

        logging_manager.create_log(
            'INFO',
            f"Ticket created: {interaction.user} ({interaction.user.id}) "
            f"opened ticket {thread.id}"
        )

        await interaction.followup.send(
            content=DESCRIPTIONS['ticket_created'].format(thread.mention),
            ephemeral=True
        )


class CloseTicketView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Close", emoji="🔒", style=ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "other"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to close "
                f"ticket {interaction.channel.id}"
            )
            return await interaction.followup.send(
                content=ERRORS[error_key],
                ephemeral=True
            )

        guild_id = interaction.guild.id
        manager = TicketManager(guild_id)

        ticket_details: Ticket = manager.get_ticket(interaction.channel.id)

        manager.close_ticket(
            interaction.channel.id,
            interaction.user.id
        )

        logging_manager.create_log(
            'INFO',
            f"Ticket closed: Ticket {interaction.channel.id} closed by "
            f"{interaction.user} ({interaction.user.id})"
        )

        user = interaction.guild.get_member(ticket_details.user_id)
        settings: TicketSettings = TicketSettingsManager(guild_id).get_settings()
        transcript_channel = interaction.guild.get_channel(settings.transcripts_channel_id)

        embed = create_embed(
            author_name="Transcript",
            fields=[
                ("Ticket", f"{interaction.channel.name} `{interaction.channel.id}`", False),
                ("Reason", ticket_details.reason, False),
                ("Created At", f"<t:{ticket_details.created_at}:R>", False),
                ("User", f"{user.name} `{user.id}`", False),
                ("Closed By", f"{interaction.user.name} `{interaction.user.id}`", False)
            ],
            thumbnail=user.display_avatar.url if user and user.display_avatar else None
        )

        if transcript_channel:
            await transcript_channel.send(embed=embed)

        await interaction.followup.send(
            content=DESCRIPTIONS['ticket_closed'].format(interaction.user.name),
            ephemeral=True
        )

        await asyncio.sleep(1)
        await interaction.channel.delete()