from discord import ButtonStyle, Client, Interaction
from discord.ui import Button, View, button

from content import DESCRIPTIONS
from database import Ticket
from database.handlers import LoggingManager, TicketManager
from .modals import TicketReasonModal


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
                "INFO", f"Ticket creation blocked: {interaction.user} ({interaction.user.id}) already has open ticket {ticket.channel_id}"
            )
            return await interaction.response.send_message(
                content=DESCRIPTIONS['ticket_already_open'].format(ticket.channel_id),
                ephemeral=True
            )

        await interaction.response.send_modal(TicketReasonModal(self.client))