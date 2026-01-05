from discord import Interaction, ButtonStyle, Message, TextStyle
from discord.ui import View, button, Button, Modal, TextInput

from ui import normal, log_embed
from core import LOGO
from core.utils import format_duration
from database.handlers import CaseManager


class CaseView(View):
    def __init__(
        self, 
        org_interaction: Interaction, 
        org_user: int,
        case_id: str,
        timeout: int = 300
    ):
        super().__init__(timeout=timeout)
        self._interaction = org_interaction
        self._org_user = org_user
        self._case_id = case_id

    @button(
        label="Delete case",
        style=ButtonStyle.red,
        custom_id="case_delete"
    )
    async def delete(self, interaction: Interaction, button: Button):
        await interaction.response.defer()

        embed = normal(
            author_name="Confirm",
            author_icon_url=LOGO,
            description="Are you sure you want to delete this case?",
            footer="You have 60 seconds to confirm"
        )

        view = ConfirmView(
            self._interaction,
            self._org_user,
            self._case_id
        )

        msg = await interaction.followup.send(
            embed=embed,
            view=view,
            ephemeral=True,
            wait=True
        )

        view._message = msg


    @button(
        label="Edit reason",
        style=ButtonStyle.gray,
        custom_id="edit_case_reason"
    )
    async def edit_reason(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(
            EditReasonModal(
                self._interaction, self._case_id, self
            )
        )

    async def interaction_check(self, interaction: Interaction):
        if self._org_user == 0:
            return True
        
        if interaction.user.id != self._org_user:
            return False

        return True

    async def on_timeout(self):
        self.clear_items()
        await self._interaction.edit_original_response(view=None)    


class ConfirmView(View):
    def __init__(
        self,
        org_interaction: Interaction,
        org_user: int,
        case_id: str,
        timeout: int = 60
    ):
        super().__init__(timeout=timeout)
        self._interaction = org_interaction
        self._org_user = org_user
        self.case_id = case_id
        self._message: Message | None = None

    @button(
        label=f"Confirm",
        style=ButtonStyle.green,
        custom_id="case_delete_confirm"
    )
    async def confirm(
        self,
        interaction: Interaction,
        button: Button
    ):
        await interaction.response.defer()

        CaseManager(interaction.guild.id).delete_case(self.case_id)
        await self._message.delete()

        await self._interaction.edit_original_response(
            embed=normal(
                author_name="Case deleted", author_icon_url=LOGO,
                description="You have successfully deleted this case."
            ),
            view=None,
        )

    @button(
        label=f"Cancel",
        style=ButtonStyle.gray,
        custom_id="case_delete_cancel"
    )
    async def cancel(
        self,
        interaction: Interaction,
        button: Button
    ):
        await interaction.response.defer()
        await self._message.delete()

    async def on_timeout(self):
        if self._message:
            await self._message.delete()



class EditReasonModal(Modal, title="Edit case reason"):
    reason = TextInput(
        label="Edit Reason",
        style=TextStyle.paragraph,
        required=True,
        min_length=3,
        max_length=512
    )

    def __init__(
        self, 
        interaction: Interaction,
        case_id: str, 
        view: View
    ):
        super().__init__()
        self._interaction = interaction
        self._case_id = case_id,
        self._view = view

    async def on_submit(self, interaction: Interaction):
        new_reason = str(self.reason).strip()

        CaseManager(self._interaction.guild.id).update_reason(self._case_id, new_reason)

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(self._case_id)  

        fields = [
            ("user", f"<@{case.user_id}> `{case.user_id}`", True),
            ("moderator", f"<@{case.moderator_id}> `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("duration", f"{format_duration(case.duration)}", False))

        fields.append(("reason", case.reason, False))

        await self._interaction.edit_original_response(
            embed=log_embed(
                author_name=f"{case.type} [{case.case_id}]",
                fields=fields
            ),
            view=self._view
        )

        await interaction.response.send_message(
            embed=normal(
                author_name="Reason edited",
                author_icon_url=LOGO,
                description="You have successfully edited the reason"
            ),
            delete_after=30,
            ephemeral=True
        )


        