from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput, View

from content import DESCRIPTIONS, ERRORS
from core.utils import format_duration
from database.handlers import CaseManager, LoggingManager
from ui import create_embed


from discord import Interaction, TextStyle, Message
from discord.ui import Modal, TextInput, View

from content import DESCRIPTIONS
from core.utils import format_duration
from database.handlers import CaseManager, LoggingManager
from ui import create_embed


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
        case_id: str,
        message: Message,
        view: View
    ):
        super().__init__()
        self._case_id = case_id
        self._message = message
        self._view = view

    async def on_submit(self, interaction: Interaction):
        new_reason = str(self.reason).strip()

        logging_manager = LoggingManager(interaction.guild.id)
        manager = CaseManager(interaction.guild.id)

        manager.update_reason(self._case_id, new_reason)

        logging_manager.create_log(
            'INFO',
            f"Case updated: Reason updated for case {self._case_id} by "
            f"{interaction.user} ({interaction.user.id})"
        )

        case = manager.get_case(self._case_id)
        guild = interaction.guild

        user = guild.get_member(case.user_id)
        moderator = guild.get_member(case.moderator_id) if case.moderator_id else None

        fields = [
            ("User", f"{user.name if user else 'Unknown User'} `{case.user_id}`", True),
            ("Moderator", f"{moderator.name if moderator else 'System'} `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("Duration", format_duration(case.duration), False))

        fields.append(("Reason", case.reason, False))

        await self._message.edit(
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
        if str(self.confirm).lower() != "confirm":
            await interaction.response.send_message(
                content=ERRORS["confirm_error"],
                ephemeral=True
            )
            return

        logging_manager = LoggingManager(interaction.guild.id)
        manager = CaseManager(interaction.guild.id)

        deleted = manager.clear_user_cases(self._member_id)

        logging_manager.create_log(
            "INFO",
            f"Cases cleared: {deleted} cases for user ID {self._member_id} "
            f"cleared by {interaction.user} ({interaction.user.id})"
        )

        await interaction.response.send_message(
            content=DESCRIPTIONS["cases_cleared"].format(deleted),
            ephemeral=True
        )


class ConfirmCaseDeleteModal(Modal, title="Confirm"):
    confirm = TextInput(
        label="Type 'confirm' to confirm",
        placeholder="confirm",
        style=TextStyle.short,
        required=True,
        min_length=7,
        max_length=7
    )

    def __init__(self, case_id: str, message: Message):
        super().__init__()
        self._case_id = case_id
        self._message = message

    async def on_submit(self, interaction: Interaction):
        if str(self.confirm).lower() != "confirm":
            await interaction.response.send_message(
                content=ERRORS["confirm_error"],
                ephemeral=True
            )
            return

        logging_manager = LoggingManager(interaction.guild.id)
        manager = CaseManager(interaction.guild.id)

        manager.delete_case(self._case_id)

        logging_manager.create_log(
            "INFO",
            f"Case deleted: Case {self._case_id} deleted by "
            f"{interaction.user} ({interaction.user.id})"
        )

        await self._message.edit(
            content=DESCRIPTIONS["case_deleted"],
            embed=None,
            view=None
        )

        await interaction.response.send_message(
            content=DESCRIPTIONS["case_deleted"],
            ephemeral=True
        )