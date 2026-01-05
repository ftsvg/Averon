from discord.ext import commands
from discord import app_commands, Interaction, TextChannel

from content import COMMANDS, COMMAND_ERRORS
from core import check_permissions, LOGO
from core.utils import format_duration
from ui import log_embed, error, normal
from ui.views import CaseView
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
        await interaction.response.defer()

        if not await check_permissions(interaction, "warn"):
            return
        
        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)  

        if not case:
            return await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["case_not_found"]["title"],
                    description=COMMAND_ERRORS["case_not_found"]["message"]
                )
            )

        guild = interaction.guild    
        user = guild.get_member(case.user_id)
        moderator = guild.get_member(case.moderator_id) if case.moderator_id else None

        fields = [
            ("user", f"{user.name if user else 'Unknown User'} `{case.user_id}`", True),
            ("moderator", f"{moderator.name if moderator else 'System'} `{case.moderator_id}`" if case.moderator_id else "System", True),
        ]

        if case.duration:
            fields.append(("duration", f"{format_duration(case.duration)}", False))

        fields.append(("reason", case.reason, False))

        await interaction.edit_original_response(
            embed=log_embed(
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
        await interaction.response.defer()

        if not await check_permissions(interaction, "warn"):
            return

        manager = CaseManager(interaction.guild.id)
        case = manager.get_case(case_id)

        if not case:
            return await interaction.edit_original_response(
                embed=error(
                    title=COMMAND_ERRORS["case_not_found"]["title"],
                    description=COMMAND_ERRORS["case_not_found"]["message"]
                )
            )
        
        manager.delete_case(case_id)

        await interaction.edit_original_response(
            embed=normal(
                author_name="Case deleted", author_icon_url=LOGO,
                description="You have successfully deleted this case."
            )
        )
        
        
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Case(client))