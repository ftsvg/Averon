from discord import (
    ButtonStyle,
    Embed,
    Interaction,
    Member
)
from discord.ui import Button, View, button

from database import Case
from ui import create_embed


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