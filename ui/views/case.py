from discord import (
    ButtonStyle,
    Embed,
    Interaction,
    Member,
    Message,
    TextStyle,
)
from discord.ui import Button, Modal, TextInput, View, button

from content import DESCRIPTIONS, ERRORS
from core.utils import format_duration
from database import Case
from database.handlers import CaseManager, LoggingManager
from ui import create_embed


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
        if not interaction.response.is_done():
            await interaction.response.defer()

        embed = create_embed(
            author_name="Confirm",
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
                self._interaction,
                self._case_id,
                self
            )
        )

    async def interaction_check(self, interaction: Interaction):
        if self._org_user == 0:
            return True
        return interaction.user.id == self._org_user

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
        label="Confirm",
        style=ButtonStyle.green,
        custom_id="case_delete_confirm"
    )
    async def confirm(self, interaction: Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        CaseManager(interaction.guild.id).delete_case(self.case_id)

        logging_manager.create_log(
            'INFO',
            f"Case deleted: Case {self.case_id} deleted by "
            f"{interaction.user} ({interaction.user.id})"
        )

        await self._message.delete()
        self._message = None
        self.stop()

        await self._interaction.edit_original_response(
            content=DESCRIPTIONS['case_deleted'],
            embed=None,
            view=None
        )

    @button(
        label="Cancel",
        style=ButtonStyle.gray,
        custom_id="case_delete_cancel"
    )
    async def cancel(self, interaction: Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer()

        await self._message.delete()
        self._message = None
        self.stop()

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
        self._case_id = case_id
        self._view = view

    async def on_submit(self, interaction: Interaction):
        new_reason = str(self.reason).strip()

        logging_manager = LoggingManager(interaction.guild.id)

        CaseManager(self._interaction.guild.id).update_reason(
            self._case_id,
            new_reason
        )

        logging_manager.create_log(
            'INFO',
            f"Case updated: Reason updated for case {self._case_id} by "
            f"{interaction.user} ({interaction.user.id})"
        )

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(self._case_id)

        guild = self._interaction.guild
        user = guild.get_member(case.user_id)
        moderator = guild.get_member(case.moderator_id) if case.moderator_id else None

        fields = [
            ("User", f"{user.name if user else 'Unknown User'} `{case.user_id}`", True),
            ("Moderator", f"{moderator.name if moderator else 'System'} `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("Duration", format_duration(case.duration), False))

        fields.append(("Reason", case.reason, False))

        await self._interaction.edit_original_response(
            embed=create_embed(
                author_name=f"{case.type} [{case.case_id}]",
                fields=fields
            ),
            view=self._view
        )

        await interaction.response.send_message(
            content=DESCRIPTIONS['case_reason_edited'],
            ephemeral=True
        )


class ConfirmCaseClearModal(Modal, title="Confirm"):
    confirm = TextInput(
        label="Type 'confirm' to confirm",
        placeholder="confirm",
        style=TextStyle.short,
        required=True,
        min_length=7,
        max_length=7
    )

    def __init__(self, member_id: int):
        super().__init__()
        self._member_id = member_id

    async def on_submit(self, interaction: Interaction):
        if str(self.confirm).lower() != 'confirm':
            return await interaction.response.send_message(
                content=ERRORS['confirm_error'],
                ephemeral=True
            )

        logging_manager = LoggingManager(interaction.guild.id)

        manager = CaseManager(interaction.guild.id)
        deleted = manager.clear_user_cases(self._member_id)

        logging_manager.create_log(
            'INFO',
            f"Cases cleared: {deleted} cases for user ID {self._member_id} "
            f"cleared by {interaction.user} ({interaction.user.id})"
        )

        await interaction.response.send_message(
            content=DESCRIPTIONS['cases_cleared'].format(deleted),
            ephemeral=True
        )


class CasePagination(View):
    def __init__(
        self,
        org_interaction: Interaction,
        org_user: int,
        member: Member,
        cases: list[Case],
        header: str,
        timeout: int = 120
    ):
        super().__init__(timeout=timeout)
        self._interaction = org_interaction
        self._org_user = org_user
        self._member = member
        self._cases = cases
        self.header = header
        self.page = 0
        self.per_page = 5
        self.max_page = (len(self._cases) - 1) // self.per_page
        self.update_buttons()

    def build_embed(self) -> Embed:
        start = self.page * self.per_page
        end = start + self.per_page

        lines = [
            f"> {case.type} `[{case.case_id}]` - <t:{case.created_at}:R>"
            for case in self._cases[start:end]
        ]

        return create_embed(
            author_name="Case history",
            description=self.header + "\n".join(lines),
            footer=f"Page {self.page + 1}/{self.max_page + 1}"
        )

    def update_buttons(self):
        self.prev_page.disabled = self.page == 0
        self.next_page.disabled = self.page >= self.max_page

    @button(label="Previous", style=ButtonStyle.gray)
    async def prev_page(self, interaction: Interaction, button: Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @button(label="Next", style=ButtonStyle.gray)
    async def next_page(self, interaction: Interaction, button: Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    async def interaction_check(self, interaction: Interaction):
        return interaction.user.id == self._org_user

    async def on_timeout(self):
        self.clear_items()
        await self._interaction.edit_original_response(view=None)