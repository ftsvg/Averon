from discord import (
    AllowedMentions,
    Client,
    Interaction,
    PermissionOverwrite,
    TextStyle,
)
from discord.ui import Modal, TextInput

from content import DESCRIPTIONS, ERRORS
from database import Ticket, TicketSettings
from database.handlers import (
    LoggingManager,
    TicketManager,
    TicketSettingsManager,
)
from ui import create_embed
from .close import TicketCloseButton


class TicketReasonModal(Modal, title="Support ticket"):
    reason = TextInput(
        label="Ticket reason",
        placeholder="Your reason here:",
        style=TextStyle.paragraph,
        required=True,
        min_length=3,
        max_length=512
    )

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        user = interaction.user
        guild_id = guild.id

        logging_manager = LoggingManager(guild_id)
        manager = TicketManager(guild_id)
        settings: TicketSettings = TicketSettingsManager(guild_id).get_settings()

        if (
            settings is None
            or settings.staff_role_id is None
            or settings.ticket_category_id is None
            or settings.transcripts_channel_id is None
        ):
            logging_manager.create_log(
                "ERROR",
                f"Ticket creation failed: ticket system not configured "
                f"(requested by {user} ({user.id}))"
            )
            await interaction.response.send_message(
                content=ERRORS["ticket_config_not_set_error"],
                ephemeral=True
            )
            return

        category = guild.get_channel(settings.ticket_category_id)
        staff_role = guild.get_role(settings.staff_role_id)

        if category is None or staff_role is None:
            logging_manager.create_log(
                "ERROR",
                f"Ticket creation failed: ticket system not configured "
                f"(requested by {user} ({user.id}))"
            )
            await interaction.response.send_message(
                content=ERRORS["ticket_config_not_set_error"],
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
            user: PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            staff_role: PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}".lower(),
            category=category,
            overwrites=overwrites,
            reason=f"Support ticket opened by {user} ({user.id})"
        )

        ticket_id = manager.create_ticket(
            user_id=user.id,
            channel_id=channel.id,
            reason=self.reason.value
        )

        await channel.send(
            content=f"Welcome {user.mention}!",
            allowed_mentions=AllowedMentions(users=True),
            embed=create_embed(
                author_name=f"support ticket [{ticket_id}]",
                description=(
                    "A staff member will assist you shortly.\n"
                    "Please describe your issue in detail."
                ),
                fields=[
                    ("User", f"{user.name} `{user.id}`", False),
                    ("Reason", self.reason.value, False),
                ],
                thumbnail=user.display_avatar.url if user.display_avatar else None
            ),
            view=TicketCloseButton(self.client)
        )

        logging_manager.create_log(
            "INFO",
            f"Ticket created: {user} ({user.id}) opened ticket "
            f"{channel.id} [{ticket_id}]"
        )

        await interaction.response.send_message(
            content=DESCRIPTIONS["ticket_created"].format(channel.mention),
            ephemeral=True
        )