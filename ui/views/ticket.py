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

from database.handlers import TicketManager, TicketSettingsManager
from database import Ticket, TicketSettings
from ui import error, normal, log_embed
from content import COMMAND_ERRORS
from core import LOGO, check_ticket_config_permissions


class TicketsView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Create ticket", style=ButtonStyle.gray, custom_id="create_ticket")
    async def create(self, interaction: Interaction, button: Button):
        manager = TicketManager(interaction.guild.id)

        ticket: Ticket = manager.get_ticket_by_user(interaction.user.id)
        if ticket:
            return await interaction.response.send_message(
                embed=error(
                    description=f"You already have an open ticket at <#{ticket.channel_id}>"
                ),
                ephemeral=True,
                delete_after=30
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
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild.id

        manager = TicketManager(guild_id)
        settings: TicketSettings = TicketSettingsManager(guild_id).get_settings()

        if (
            settings is None
            or settings.staff_role_id is None
            or settings.ticket_channel_id is None
            or settings.transcripts_channel_id is None
        ):
            return await interaction.followup.send(
                embed=error(
                    title=COMMAND_ERRORS["ticket_config_not_set_error"]["title"],
                    description=COMMAND_ERRORS["ticket_config_not_set_error"]["message"]
                ),
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
            embed=log_embed(
                author_name="Support ticket",
                description=(
                    "A staff member will assist you shortly.\n"
                    "Please provide any additional details if needed."
                ),
                fields=[
                    ("user", f"{interaction.user.name} `{interaction.user.id}`", False),
                    ("reason", self.reason.value, False)
                ],
                thumbnail=interaction.user.display_avatar.url
            ),
            view=CloseTicketView(self.client)
        )

        manager.create_ticket(
            interaction.user.id,
            thread.id,
            self.reason.value
        )

        await interaction.followup.send(
            embed=normal(
                author_name="Ticket created",
                author_icon_url=LOGO,
                description=f"You have successfully created a ticket at {thread.mention}"
            ),
            ephemeral=True
        )


class CloseTicketView(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client

    @button(label="Close", emoji="🔒", style=ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        if not await check_ticket_config_permissions(interaction, "other"):
            return

        guild_id = interaction.guild.id
        manager = TicketManager(guild_id)

        ticket_details: Ticket = manager.get_ticket(interaction.channel.id)

        manager.close_ticket(
            interaction.channel.id,
            interaction.user.id
        )

        user = interaction.guild.get_member(ticket_details.user_id)
        settings: TicketSettings = TicketSettingsManager(guild_id).get_settings()
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

        await interaction.followup.send(
            embed=normal(
                author_name="Ticket closed",
                author_icon_url=LOGO,
                description="This ticket has been closed."
            )
        )

        await asyncio.sleep(2)
        await interaction.channel.delete()