import asyncio

from discord import ButtonStyle, Client, Interaction
from discord.ui import Button, View, button

from content import DESCRIPTIONS, ERRORS
from core import check_permissions, send_transcript_log, send_user_dm
from database.handlers import LoggingManager, TicketManager
from ui import create_embed


class TicketCloseButton(View):
    def __init__(self, client: Client):
        super().__init__(timeout=None)
        self.client = client
        self.message = None

    def _bind_message(self, interaction: Interaction):
        if self.message is None:
            self.message = interaction.message

    @button(label="Close", emoji="🔒", style=ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: Interaction, button: Button):
        self._bind_message(interaction)

        await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "other"):
            logging_manager.create_log(
                "WARNING",
                f"Permission denied: {interaction.user} ({interaction.user.id}) "
                f"attempted to close ticket {interaction.channel.id}"
            )
            return await interaction.followup.send(
                content=ERRORS[error_key],
                ephemeral=True
            )

        guild_id = interaction.guild.id
        manager = TicketManager(guild_id)

        ticket_details = manager.get_ticket(interaction.channel.id)

        manager.close_ticket(interaction.channel.id, interaction.user.id)

        logging_manager.create_log(
            "INFO",
            f"Ticket closed: Ticket {interaction.channel.id} closed by "
            f"{interaction.user} ({interaction.user.id})"
        )

        user = interaction.guild.get_member(ticket_details.user_id)

        embed = create_embed(
            author_name=f"transcript [{ticket_details.ticket_id}]",
            fields=[
                ("Ticket", f"{interaction.channel.name} `{interaction.channel.id}`", False),
                ("Reason", ticket_details.reason, False),
                ("Created At", f"<t:{ticket_details.created_at}:R>", False),
                ("User", f"{user.name} `{user.id}`", False),
                ("Closed By", f"{interaction.user.name} `{interaction.user.id}`", False),
            ],
            thumbnail=user.display_avatar.url if user and user.display_avatar else None,
        )

        await send_transcript_log(interaction, embed)
        await send_user_dm(interaction, user, embed=embed)

        await interaction.followup.send(
            content=DESCRIPTIONS["ticket_closed"].format(interaction.user.name)
        )

        await asyncio.sleep(1)
        await interaction.channel.delete()