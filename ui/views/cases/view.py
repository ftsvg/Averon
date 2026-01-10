from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button

from .modals import ConfirmCaseDeleteModal, EditReasonModal


class CaseView(View):
    def __init__(
        self,
        org_user: int,
        case_id: str,
        timeout: int = 300
    ):
        super().__init__(timeout=timeout)
        self._org_user = org_user
        self._case_id = case_id
        self.message = None

    def _bind_message(self, interaction: Interaction):
        if self.message is None:
            self.message = interaction.message

    @button(label="Delete case", style=ButtonStyle.red)
    async def delete(self, interaction: Interaction, button: Button):
        self._bind_message(interaction)

        await interaction.response.send_modal(
            ConfirmCaseDeleteModal(
                case_id=self._case_id,
                message=self.message
            )
        )

    @button(label="Edit reason", style=ButtonStyle.gray)
    async def edit_reason(self, interaction: Interaction, button: Button):
        self._bind_message(interaction)

        await interaction.response.send_modal(
            EditReasonModal(
                case_id=self._case_id,
                message=self.message,
                view=self
            )
        )

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self._org_user == 0 or interaction.user.id == self._org_user

    async def on_timeout(self):
        if self.message:
            self.clear_items()
            await self.message.edit(view=None)