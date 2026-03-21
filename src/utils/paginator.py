"""
Shared paginated cv2 LayoutView for use across cogs.

Usage:
    pages = ["line1\nline2", "line3\nline4"]   # one string per page
    view = PaginatedView(title="My Title", pages=pages)
    await ctx.send(view=view)
"""
import discord


class _PrevButton(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(
            label="◀",
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        v: PaginatedView = self.view
        v.current_page -= 1
        v._build()
        await interaction.response.edit_message(view=v)


class _PageLabel(discord.ui.Button):
    def __init__(self, label: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            disabled=True,
        )

    async def callback(self, interaction: discord.Interaction):
        pass


class _NextButton(discord.ui.Button):
    def __init__(self, disabled: bool):
        super().__init__(
            label="▶",
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        v: PaginatedView = self.view
        v.current_page += 1
        v._build()
        await interaction.response.edit_message(view=v)


class PaginatedView(discord.ui.LayoutView):
    """
    A cv2 LayoutView that paginates a list of page strings.

    Parameters
    ----------
    title : str
        Heading shown at the top of each page.
    pages : list[str]
        One formatted string per page (pre-chunked by the caller).
    icon_url : str | None
        If given, a Thumbnail is added via a Section accessory.
    timeout : float
        How long (seconds) before the buttons expire.
    """

    def __init__(
        self,
        *,
        title: str,
        pages: list[str],
        icon_url: str | None = None,
        timeout: float = 180,
    ):
        super().__init__(timeout=timeout)
        self.title = title
        self.pages = pages
        self.icon_url = icon_url
        self.current_page = 0
        self._build()

    def _build(self):
        self.clear_items()

        total = len(self.pages)
        content = f"### {self.title}\n{self.pages[self.current_page]}"
        footer = f"-# Page {self.current_page + 1} / {total}"

        if self.icon_url:
            container = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(content=content),
                    accessory=discord.ui.Thumbnail(self.icon_url),
                ),
                discord.ui.TextDisplay(content=footer),
            )
        else:
            container = discord.ui.Container(
                discord.ui.TextDisplay(content=content),
                discord.ui.TextDisplay(content=footer),
            )

        self.add_item(container)

        if total > 1:
            self.add_item(discord.ui.ActionRow(
                _PrevButton(disabled=self.current_page == 0),
                _PageLabel(label=f"{self.current_page + 1} / {total}"),
                _NextButton(disabled=self.current_page == total - 1),
            ))


def paginate(items: list[str], per_page: int = 10) -> list[str]:
    """
    Chunk a flat list of strings into page strings.

    Each page is a newline-joined block of `per_page` items.
    """
    pages = []
    for i in range(0, len(items), per_page):
        pages.append("\n".join(items[i : i + per_page]))
    return pages
