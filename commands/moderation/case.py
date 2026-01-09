from discord import Interaction, Member, app_commands
from discord.ext import commands

from content import COMMANDS, DESCRIPTIONS, ERRORS
from core import check_permissions
from core.utils import format_duration
from database.handlers import CaseManager, LoggingManager
from ui import create_embed
from ui.views import CasePagination, CaseView, ConfirmCaseClearModal


class Case(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    case = app_commands.Group(
        name='case',
        description='Case related commands.',
    )


    @case.command(
        name=COMMANDS['case_view']['name'],
        description=COMMANDS['case_view']['description']
    )
    @app_commands.describe(case_id=COMMANDS["case_view"]["case_id"])
    async def view(self, interaction: Interaction, case_id: str):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "warn"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to view case {case_id}"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)

        if not case:
            logging_manager.create_log(
                'INFO',
                f"Case view failed: Case {case_id} does not exist "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.edit_original_response(
                content=ERRORS['case_not_found']
            )

        guild = interaction.guild
        user = guild.get_member(case.user_id)
        moderator = guild.get_member(case.moderator_id) if case.moderator_id else None

        fields = [
            ("User", f"{user.name if user else 'Unknown'} `{case.user_id}`", True),
            ("Moderator", f"{moderator.name if moderator else 'System'} `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("Duration", format_duration(case.duration), False))

        fields.append(("Reason", case.reason, False))

        await interaction.edit_original_response(
            embed=create_embed(
                author_name=f"{case.type} [{case.case_id}]",
                fields=fields
            ),
            view=CaseView(
                interaction,
                interaction.user.id,
                case.case_id
            )
        )


    @case.command(
        name=COMMANDS["case_delete"]["name"],
        description=COMMANDS["case_delete"]["description"]
    )
    @app_commands.describe(case_id=COMMANDS["case_delete"]["case_id"])
    async def delete(self, interaction: Interaction, case_id: str):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "warn"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to delete case {case_id}"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)

        if not case:
            logging_manager.create_log(
                'INFO',
                f"Case deletion failed: Case {case_id} does not exist "
                f"(requested by {interaction.user} ({interaction.user.id}))"
            )
            return await interaction.edit_original_response(
                content=ERRORS['case_not_found']
            )

        manager.delete_case(case_id)

        logging_manager.create_log(
            'INFO',
            f"Case deleted: Case {case_id} deleted by {interaction.user} ({interaction.user.id})"
        )

        await interaction.edit_original_response(
            content=DESCRIPTIONS['case_deleted']
        )


    @case.command(
        name=COMMANDS["case_clear"]["name"],
        description=COMMANDS["case_clear"]["description"]
    )
    @app_commands.describe(member=COMMANDS["case_clear"]["member"])
    async def clear(self, interaction: Interaction, member: Member):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "warn"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to clear cases for "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        await interaction.response.send_modal(
            ConfirmCaseClearModal(member.id)
        )


    @case.command(
        name=COMMANDS["case_history"]["name"],
        description=COMMANDS["case_history"]["description"]
    )
    @app_commands.describe(member=COMMANDS["case_history"]["member"])
    async def history(self, interaction: Interaction, member: Member):
        if not interaction.response.is_done():
            await interaction.response.defer()

        logging_manager = LoggingManager(interaction.guild.id)

        if error_key := await check_permissions(interaction, "warn"):
            logging_manager.create_log(
                'WARNING',
                f"Permission denied: {interaction.user} ({interaction.user.id}) attempted to view case history for "
                f"{member} ({member.id})"
            )
            return await interaction.edit_original_response(
                content=ERRORS[error_key]
            )

        manager = CaseManager(interaction.guild.id)
        cases = manager.get_user_cases(member.id)

        if not cases:
            return await interaction.edit_original_response(
                content=ERRORS['no_cases_error']
            )

        header = f"**{member.name}** has a total of `{len(cases)}` cases.\n\n**Cases**\n"

        if len(cases) > 5:
            view = CasePagination(
                org_interaction=interaction,
                org_user=interaction.user.id,
                member=member,
                cases=cases,
                header=header
            )
            embed = view.build_embed()
        else:
            view = None
            lines = [
                f"> {case.type} `[{case.case_id}]` - <t:{case.created_at}:R>"
                for case in cases
            ]
            embed = create_embed(
                author_name="Case history",
                description=header + "\n".join(lines)
            )

        await interaction.edit_original_response(
            embed=embed,
            view=view
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Case(client))
