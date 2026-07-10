"""
Economy — leaderboard command.
"""
import asyncio

import discord
from discord.ext import commands
from ..data import (
    _info_view, _card_view,
    render_leaderboard_card, fetch_avatar_bytes,
)


class LeaderboardMixin:
    """leaderboard command."""

    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"],
        description="See the café rich list as image cards",
        help="{ 'en': 'see who has the most treats 🏆🥐', 'de': 'sieh die reichsten Gäste', 'es': 'mira quién tiene más 🏆🥐' }"
    )
    async def leaderboard(self, ctx: commands.Context):
        sorted_users = sorted(
            self.economy_data.items(),
            key=lambda x: x[1].get("balance", 0) + x[1].get("bank", 0),
            reverse=True,
        )
        if not sorted_users:
            return await ctx.send(view=_info_view("☕ Quiet café", "No one has any coins yet — the café is just opening!"))
        # paginate full sorted list into pages of 10
        per_page = 10
        pages_src = [sorted_users[i : i + per_page] for i in range(0, len(sorted_users), per_page)]

        async def _entry(i, uid, d):
            user = self.bot.get_user(int(uid)) or None
            if user is None and uid.isdigit():
                try:
                    user = await self.bot.fetch_user(int(uid))
                except Exception:
                    user = None
            avatar = None
            name = uid
            if user is not None:
                avatar = await fetch_avatar_bytes(str(user.display_avatar.replace(size=128, format="png")), size=128)
                name = user.display_name if hasattr(user, "display_name") else user.name
            return {"rank": i + 1, "name": name, "total": int(d.get("balance", 0) + d.get("bank", 0)), "avatar": avatar}

        # build entries for each page (list of list[dict])
        pages_entries = []
        for p_index, page in enumerate(pages_src):
            start_idx = p_index * per_page
            entries = await asyncio.gather(*(_entry(i, uid, d) for i, (uid, d) in enumerate(page, start=start_idx)))
            pages_entries.append(entries)

        total_pages = len(pages_entries)

        # nested view with deferred button handling
        class _PrevButton(discord.ui.Button):
            def __init__(self, disabled: bool):
                super().__init__(label="◀", style=discord.ButtonStyle.secondary, disabled=disabled)

            async def callback(self, interaction: discord.Interaction):
                v: _CardView = self.view
                if v.current_page == 0:
                    return await interaction.response.defer()
                v.current_page -= 1
                await interaction.response.defer()
                buf = await render_leaderboard_card(title="🏆 Café Rich List", entries=v.pages[v.current_page], page=v.current_page + 1, pages=total_pages)
                v._build()
                await interaction.message.edit(view=v, attachments=[discord.File(buf, "leaderboard.png")], allowed_mentions=discord.AllowedMentions.none())


        class _NextButton(discord.ui.Button):
            def __init__(self, disabled: bool):
                super().__init__(label="▶", style=discord.ButtonStyle.secondary, disabled=disabled)

            async def callback(self, interaction: discord.Interaction):
                v: _CardView = self.view
                if v.current_page >= len(v.pages) - 1:
                    return await interaction.response.defer()
                v.current_page += 1
                await interaction.response.defer()
                buf = await render_leaderboard_card(title="🏆 Café Rich List", entries=v.pages[v.current_page], page=v.current_page + 1, pages=total_pages)
                v._build()
                await interaction.message.edit(view=v, attachments=[discord.File(buf, "leaderboard.png")], allowed_mentions=discord.AllowedMentions.none())


        class _PageLabel(discord.ui.Button):
            def __init__(self, label: str):
                super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=True)


        class _CardView(discord.ui.LayoutView):
            def __init__(self, pages: list[list[dict]]):
                super().__init__(timeout=180)
                self.pages = pages
                self.current_page = 0
                self._build()

            def _build(self):
                self.clear_items()
                total = len(self.pages)
                container = discord.ui.Container(
                    discord.ui.TextDisplay(content=f"### 🏆 Leaderboard"),
                    discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://leaderboard.png")),
                )
                container.add_item(discord.ui.TextDisplay(content=f"-# Showing top **{min(len(sorted_users), per_page)}** of **{len(sorted_users)}** café-goers."))

                if total > 1:
                    container.add_item(discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small))
                    container.add_item(discord.ui.ActionRow(
                        _PrevButton(disabled=self.current_page == 0),
                        _PageLabel(label=f"{self.current_page + 1} / {total}"),
                        _NextButton(disabled=self.current_page == total - 1),
                    ))

                self.add_item(container)

        # render first page and send with the paginated view
        first_buf = await render_leaderboard_card(title="🏆 Café Rich List", entries=pages_entries[0], page=1, pages=total_pages)
        view = _CardView(pages_entries)
        await ctx.send(view=view, file=discord.File(first_buf, "leaderboard.png"), allowed_mentions=discord.AllowedMentions.none())
