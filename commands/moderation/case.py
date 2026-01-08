from discord.ext import commands
from discord import app_commands, Interaction, Member

from content import COMMANDS, ERRORS, DESCRIPTIONS
from core import check_permissions
from core.utils import format_duration
from ui import create_embed
from ui.views import CaseView, ConfirmCaseClearModal, CasePagination
from database.handlers import CaseManager


class Case(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    case = app_commands.Group(
        name='case',
        description='Case related commands.',
    )

    @case.command(
        name=COMMANDS['case_view']['name'],
        description=COMMANDS['case_view']['description']
    )
    @app_commands.describe(
        case_id=COMMANDS["case_view"]["case_id"]
    )
    async def view(
        self,
        interaction: Interaction,
        case_id: str
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := await check_permissions(interaction, "warn"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )
        
        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)  

        if not case:
            return await interaction.edit_original_response(
                content=ERRORS['case_not_found']
            )

        guild = interaction.guild    
        user = guild.get_member(case.user_id)
        moderator = guild.get_member(case.moderator_id) if case.moderator_id else 'System'

        fields = [
            ("user", f"{user.name if user else 'Unknown user'} `{case.user_id}`", True),
            ("moderator", f"{moderator.name} `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("duration", f"{format_duration(case.duration)}", False))

        fields.append(("reason", case.reason, False))

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
    @app_commands.describe(
        case_id=COMMANDS["case_delete"]["case_id"]
    )
    async def delete(
        self,
        interaction: Interaction,
        case_id: str
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := await check_permissions(interaction, "warn"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)

        if not case:
            return await interaction.edit_original_response(
                content = ERRORS['case_not_found']
            )
        
        manager.delete_case(case_id)

        await interaction.edit_original_response(
            content=DESCRIPTIONS['case_deleted']
        )
        

    @case.command(
        name=COMMANDS["case_clear"]["name"],
        description=COMMANDS["case_clear"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["case_clear"]["member"]
    )
    async def clear(
        self,
        interaction: Interaction,
        member: Member
    ):
        if error_key := await check_permissions(interaction, "warn"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
            )
        
        await interaction.response.send_modal(
            ConfirmCaseClearModal(
                member.id
            )
        )
        

    @case.command(
        name=COMMANDS["case_history"]["name"],
        description=COMMANDS["case_history"]["description"]
    )
    @app_commands.describe(
        member=COMMANDS["case_history"]["member"]
    )
    async def history(
        self,
        interaction: Interaction,
        member: Member
    ):
        if not interaction.response.is_done():
            await interaction.response.defer()

        if error_key := await check_permissions(interaction, "warn"):
            return await interaction.edit_original_response(
                content = ERRORS[error_key]
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