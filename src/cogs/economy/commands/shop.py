"""
Economy — shop commands (shop, buy, sell, use, inventory).
"""
import discord
from discord.ext import commands
from ..data import (
    _info_view, _card_view, _reply, _check_achievements, locale_t,
    ACCENT_BROWN,
    SHOP_ITEMS, get_item, get_emoji,
    add_xp, bank_name, bank_cap, bank_rate, max_bank_tier,
)
from utils.image.economy_card import render_shop_card, render_inventory_card, fetch_avatar_bytes

from utils.command_locales import command_texts
from utils.i18n import get_lang
from utils.locales import load_locales

CMDS = command_texts(__package__)

# Niko's own emojis are filled into the catalogue's `{cross}`-style tokens by
# locale_t(), so a re-uploaded emoji id never has to be baked into three files.
_t = locale_t(load_locales("cogs.economy", "shop"))


class _ShopActionView(discord.ui.LayoutView):
    """Shop card controls; the buttons open user-only transaction panels.

    The buttons carry fixed custom ids, so the view is registered once at
    startup (see EconomyCog.cog_load) and every shop message posted since then
    keeps working after a restart without storing any message ids.
    """

    def __init__(self, cog, *, lang: str = "en", timeout: float | None = None, image_name: str = "shop.png"):
        super().__init__(timeout=timeout)
        self.cog = cog
        container = discord.ui.Container(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{image_name}")),
            discord.ui.TextDisplay(content=_t(lang, "hint_action")),
            discord.ui.ActionRow(
                discord.ui.Button(label=_t(lang, "btn_buy"), style=discord.ButtonStyle.success, custom_id="economy:shop:buy"),
                discord.ui.Button(label=_t(lang, "btn_sell"), style=discord.ButtonStyle.secondary, custom_id="economy:shop:sell"),
            ),
            accent_colour=ACCENT_BROWN,
        )
        action_row = container.children[2]
        action_row.children[0].callback = self._buy
        action_row.children[1].callback = self._sell
        self.add_item(container)

    async def _buy(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=await _ShopTransactionView.create(
                self.cog, "buy", interaction.user.id, get_lang(interaction)),
            ephemeral=True,
        )

    async def _sell(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=await _ShopTransactionView.create(
                self.cog, "sell", interaction.user.id, get_lang(interaction)),
            ephemeral=True,
        )


class _ShopTransactionView(discord.ui.LayoutView):
    """Two-step private checkout: item first, then quantity."""

    def __init__(self, cog, mode: str, user_id: int, item_options: list[discord.SelectOption], lang: str = "en"):
        super().__init__(timeout=300)
        self.cog = cog
        self.mode = mode
        self.user_id = user_id
        self.lang = lang
        self.item_id: str | None = None
        self.amount = 1
        self.amount_select = discord.ui.Select(
            placeholder=_t(lang, "amount_placeholder"),
            options=[discord.SelectOption(label=_t(lang, "choose_item_first"), value="1")],
            disabled=True,
        )
        self.item_select = discord.ui.Select(
            placeholder=_t(lang, "select_item_buy" if mode == "buy" else "select_item_sell"),
            options=item_options,
        )
        self.item_select.callback = self._item_changed
        self.amount_select.callback = self._amount_changed
        confirm = discord.ui.Button(
            label=_t(lang, "confirm_buy" if mode == "buy" else "confirm_sell"),
            style=discord.ButtonStyle.success if mode == "buy" else discord.ButtonStyle.primary,
        )
        confirm.callback = self._confirm
        title = _t(lang, "checkout_buy_title" if mode == "buy" else "checkout_sell_title")
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"{title}\n{_t(lang, 'checkout_hint')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(self.item_select),
            discord.ui.ActionRow(self.amount_select),
            discord.ui.ActionRow(confirm),
            accent_colour=discord.Colour(0x57F287 if mode == "buy" else 0x5865F2),
        )
        self.add_item(container)

    @classmethod
    async def create(cls, cog, mode: str, user_id: int, lang: str = "en"):
        data = await cog.get_user_economy_data(user_id)
        if mode == "buy":
            source = SHOP_ITEMS.items()
        else:
            source = ((iid, get_item(iid)) for iid in data.get("inventory", {}) if get_item(iid))
        options = []
        for iid, item in source:
            if not item:
                continue
            count = int(data.get("inventory", {}).get(iid, 0))
            if mode == "buy":
                detail = _t(lang, "detail_price", price=f"{item['price']:,}")
            else:
                detail = _t(
                    lang, "detail_owned",
                    count=count,
                    price=f"{int(item.get('sell', item['price'] // 3)):,}",
                )
            options.append(discord.SelectOption(
                label=str(item["name"])[:100], value=str(iid), description=detail[:100], emoji=str(item.get("emoji", "📦")),
            ))
        if not options:
            options = [discord.SelectOption(
                label=_t(lang, "empty_inventory"),
                value="__empty",
                description=_t(lang, "empty_inventory_desc"),
            )]
        return cls(cog, mode, user_id, options[:25], lang)

    async def _item_changed(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        self.item_id = self.item_select.values[0]
        if self.item_id == "__empty":
            self.amount_select.disabled = True
            return await interaction.response.edit_message(view=self)
        data = await self.cog.get_user_economy_data(self.user_id)
        item = get_item(self.item_id)
        maximum = int(data.get("inventory", {}).get(self.item_id, 0)) if self.mode == "sell" else max(1, min(25, int(data.get("balance", 0)) // int(item["price"])))
        values = [1, 2, 5, 10, 25, maximum]
        values = sorted({value for value in values if 1 <= value <= maximum}) or [1]
        self.amount_select.options = [discord.SelectOption(label=f"{value} × {item['name']}", value=str(value)) for value in values]
        self.amount_select.disabled = False
        self.amount = values[0]
        await interaction.response.edit_message(view=self)

    async def _amount_changed(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        self.amount = int(self.amount_select.values[0])
        await interaction.response.edit_message(view=self)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        if not self.item_id or self.item_id == "__empty":
            return await interaction.response.send_message(_t(self.lang, "select_first"), ephemeral=True)
        await interaction.response.defer()
        await self.cog._complete_shop_transaction(interaction, self.mode, self.item_id, self.amount)


def _usable_options(data: dict) -> list[discord.SelectOption]:
    """Select-menu options for every usable item currently in the bag."""
    options: list[discord.SelectOption] = []
    for iid, count in data.get("inventory", {}).items():
        item = get_item(iid)
        if not item or int(count) < 1:
            continue
        if item.get("category") == "collectible" or not item.get("effect"):
            continue
        options.append(discord.SelectOption(
            label=str(item["name"])[:100],
            value=str(iid),
            description=f"x{int(count)} · {item.get('description', '')}"[:100],
            emoji=str(item.get("emoji", "📦")),
        ))
    return options[:25]


def _consume_one(data: dict, iid: str) -> None:
    """Remove one unit of an item from the bag (dropping it at zero)."""
    inv = data.setdefault("inventory", {})
    inv[iid] = int(inv.get(iid, 0)) - 1
    if inv[iid] <= 0:
        del inv[iid]


class _UseItemView(discord.ui.LayoutView):
    """Private panel that lists the user's usable items and lets them pick one."""

    def __init__(self, cog, user_id: int, options: list[discord.SelectOption], lang: str = "en"):
        super().__init__(timeout=300)
        self.cog = cog
        self.user_id = user_id
        self.lang = lang
        self.select = discord.ui.Select(placeholder=_t(lang, "use_placeholder"), options=options)
        self.select.callback = self._on_select
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"{_t(lang, 'use_title')}\n{_t(lang, 'use_hint')}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(self.select),
            accent_colour=ACCENT_BROWN,
        ))

    @classmethod
    async def create(cls, cog, user_id: int, lang: str = "en") -> "_UseItemView | None":
        data = await cog.get_user_economy_data(user_id)
        options = _usable_options(data)
        return cls(cog, user_id, options, lang) if options else None

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        iid  = self.select.values[0]
        data = await self.cog.get_user_economy_data(self.user_id)
        applied, title, body = self.cog._use_item_effect(data, iid, get_item(iid), self.lang)
        if applied:
            _consume_one(data, iid)
            await self.cog.save_user_economy_data(self.user_id)
        if _usable_options(data):
            await interaction.response.edit_message(
                view=_UseResultView(self.cog, self.user_id, title, body, self.lang))
        else:
            await interaction.response.edit_message(view=_info_view(title, body))


class _UseResultView(discord.ui.LayoutView):
    """Outcome of using an item, with a shortcut back to the picker."""

    def __init__(self, cog, user_id: int, title: str, body: str, lang: str = "en"):
        super().__init__(timeout=300)
        self.cog = cog
        self.user_id = user_id
        self.title = title
        self.body = body
        self.lang = lang
        again = discord.ui.Button(label=_t(lang, "btn_use_another"), emoji="🔁", style=discord.ButtonStyle.primary)
        close = discord.ui.Button(label=_t(lang, "btn_close"), style=discord.ButtonStyle.secondary)
        again.callback = self._again
        close.callback = self._close
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {title}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(content=body),
            discord.ui.ActionRow(again, close),
            accent_colour=ACCENT_BROWN,
        ))

    async def _again(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        panel = await _UseItemView.create(self.cog, self.user_id, self.lang)
        if panel is None:
            return await interaction.response.send_message(
                view=_info_view(
                    _t(self.lang, "nothing_use_title"),
                    _t(self.lang, "nothing_use_panel"),
                ),
                ephemeral=True,
            )
        await interaction.response.edit_message(view=panel)

    async def _close(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(_t(self.lang, "private_panel"), ephemeral=True)
        await interaction.response.edit_message(view=_info_view(self.title, self.body))


class ShopMixin:
    """shop, buy, sell, use, inventory commands."""

    async def _complete_shop_transaction(self, interaction: discord.Interaction, mode: str, item_id: str, count: int):
        """Validate and commit a transaction selected through the private panel."""
        lang = get_lang(interaction)
        item = get_item(item_id)
        if not item or count < 1:
            return await interaction.followup.send(view=_info_view(
                _t(lang, "invalid_sel_title"), _t(lang, "invalid_sel_body")), ephemeral=True)
        data = await self.get_user_economy_data(interaction.user.id)
        iid = item_id.lower()
        if int(data.get("level", 0)) < int(item.get("min_level", 0)):
            return await interaction.followup.send(view=_info_view(
                _t(lang, "locked_title"),
                _t(lang, "locked_body", item=item["name"], level=item["min_level"]),
            ), ephemeral=True)
        if mode == "buy":
            total = int(item["price"]) * count
            if int(data.get("balance", 0)) < total:
                return await interaction.followup.send(view=_info_view(
                    _t(lang, "no_cash_title"),
                    _t(lang, "no_cash_body", total=f"{total:,}", balance=f"{data['balance']:,}"),
                ), ephemeral=True)
            self._credit(data, -total, "buy", f"{count}x {item['name']}")
            data.setdefault("inventory", {})[iid] = int(data["inventory"].get(iid, 0)) + count
            title = _t(lang, "bought_title")
            message = _t(
                lang, "bought_body",
                count=count, emoji=item["emoji"], item=item["name"],
                total=f"{total:,}", balance=f"{data['balance']:,}",
            )
        else:
            have = int(data.setdefault("inventory", {}).get(iid, 0))
            if have < count:
                return await interaction.followup.send(view=_info_view(
                    _t(lang, "not_enough_title"), _t(lang, "not_enough_body", have=have)), ephemeral=True)
            gain = int(item.get("sell", item["price"] // 3)) * count
            self._credit(data, gain, "sell", f"{count}x {item['name']}")
            data["inventory"][iid] = have - count
            if data["inventory"][iid] <= 0:
                del data["inventory"][iid]
            title = _t(lang, "sold_title")
            message = _t(
                lang, "sold_body",
                count=count, emoji=item["emoji"], item=item["name"],
                gain=f"{gain:,}", balance=f"{data['balance']:,}",
            )
        _check_achievements(data)
        await self.save_user_economy_data(interaction.user.id)
        await interaction.followup.send(view=_info_view(title, message), ephemeral=True)

    @commands.hybrid_command(
        name="shop",
        description=CMDS.text("shop.description"),
        help=CMDS.help("shop"),
    )
    async def shop(self, ctx: commands.Context, category: str = None):
        cats = ("consumable", "upgrade", "collectible")
        lang = get_lang(ctx)
        if ctx.interaction:
            await ctx.interaction.response.defer()
        if category and category.lower() not in cats:
            view = _info_view(
                _t(lang, "unknown_cat_title"),
                _t(lang, "unknown_cat_body", cats=", ".join("`" + c + "`" for c in cats)),
            )
            return await (ctx.interaction.followup.send(view=view) if ctx.interaction else ctx.send(view=view))
        cat_filter = category.lower() if category else None
        data = await self.get_user_economy_data(ctx.author.id)
        items = [dict(item, item_id=iid) for iid, item in SHOP_ITEMS.items() if not cat_filter or item["category"] == cat_filter]
        if not items:
            view = _info_view(_t(lang, "empty_shelf_title"), _t(lang, "empty_shelf_body"))
        else:
            message = await self._show_loading_card(
                ctx, "shop", rows=len(items), shop_controls=True,
            )
            card = await render_shop_card(items=items, balance=int(data.get("balance", 0)), category=cat_filter)
            view = _ShopActionView(self, lang=lang, image_name="shop.png")
            return await message.edit(view=view, attachments=[discord.File(card, "shop.png")])
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view)
        else:
            await ctx.send(view=view)

    async def buy(self, ctx: commands.Context, item_id: str, count: int = 1):
        lang = get_lang(ctx)

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        # Ensure the amount is a positive number
        if count <= 0:
            view = _info_view(_t(lang, "bad_amount_title"), _t(lang, "bad_amount_body"))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        # Check if the item exists
        item = get_item(item_id)
        if not item:
            view = _info_view(
                _t(lang, "out_of_stock_title"), _t(lang, "no_such_item", item=item_id))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        # Check if the user meets the level requirements
        data = await self.get_user_economy_data(ctx.author.id)
        if data["level"] < item.get("min_level", 0):
            view = _info_view(
                _t(lang, "locked_title"),
                _t(lang, "locked_body", item=item["name"], level=item["min_level"]),
            )
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        # Check if the user has enough balance to buy the item
        total = item["price"] * count
        if data["balance"] < total:
            view = _info_view(
                _t(lang, "no_cash_title"),
                _t(lang, "no_cash_body_short", total=f"{total:,}", balance=f"{data['balance']:,}"),
            )
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        self._credit(data, -total, "buy", f"{count}x {item['name']}")
        inv = data["inventory"]
        inv[item_id.lower()] = int(inv.get(item_id.lower(), 0)) + count
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        view = _info_view(
            _t(lang, "bought_title"),
            _t(
                lang, "bought_body",
                count=count, emoji=item["emoji"], item=item["name"],
                total=f"{total:,}", balance=f"{data['balance']:,}",
            ),
        )
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view)
        else:
            await ctx.send(view=view)

    async def sell(self, ctx: commands.Context, item_id: str, count: int = 1):
        lang = get_lang(ctx)

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        # Verify the user provided a positive amount
        if count <= 0:
            view = _info_view(_t(lang, "bad_amount_title"), _t(lang, "bad_amount_body"))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        # Verify the item exists
        iid  = item_id.lower()
        item = get_item(iid)
        if not item:
            view = _info_view(
                _t(lang, "unknown_item_title"), _t(lang, "no_such_item", item=item_id))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        # Ensure the user has enough to sell
        data = await self.get_user_economy_data(ctx.author.id)
        have = int(data["inventory"].get(iid, 0))
        if have < count:
            view = _info_view(_t(lang, "not_enough_title"), _t(lang, "not_enough_body", have=have))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        gain = int(item.get("sell", item["price"] // 3)) * count
        self._credit(data, gain, "sell", f"{count}x {item['name']}")
        data["inventory"][iid] = have - count
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        await self.save_user_economy_data(ctx.author.id)
        view = _info_view(
            _t(lang, "sold_title"),
            _t(
                lang, "sold_body",
                count=count, emoji=item["emoji"], item=item["name"],
                gain=f"{gain:,}", balance=f"{data['balance']:,}",
            ),
        )
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view)
        else:
            await ctx.send(view=view)

    def _use_item_effect(self, data: dict, iid: str, item: dict | None, lang: str = "en") -> tuple[bool, str, str]:
        """Apply an item's effect to `data`.

        Returns ``(applied, title, body)``. When ``applied`` is True the caller
        should consume one unit of the item and save; otherwise the item is left
        untouched and the title/body explain why it could not be used.
        """
        if not item:
            return False, _t(lang, "use_unknown_title"), _t(lang, "no_such_item", item=iid)
        if int(data.get("inventory", {}).get(iid, 0)) < 1:
            return False, _t(lang, "none_in_bag_title"), _t(lang, "none_in_bag_body", item=item["name"])
        if item["category"] == "collectible":
            return False, _t(lang, "collectible_title"), _t(lang, "collectible_body")

        effect   = item.get("effect")
        msg_text = ""
        effects  = data.setdefault("effects", {})

        if effect == "work_cooldown_half":
            effects["work_cooldown_half"] = True
            msg_text = _t(lang, "fx_work_cd")
        elif effect == "crime_boost":
            effects["crime_boost"] = 1
            msg_text = _t(lang, "fx_crime")
        elif effect == "rob_shield":
            effects["rob_shield"] = 1
            msg_text = _t(lang, "fx_rob")
        elif effect == "lottery_boost":
            effects["lottery_boost"] = 1
            msg_text = _t(lang, "fx_lottery")
        elif effect == "xp_potion":
            new_lvl, _, leveled = add_xp(data, 75)
            msg_text = _t(lang, "fx_xp") + (
                _t(lang, "fx_xp_level", level=new_lvl) if leveled else "")
        elif effect == "bank_tier_up":
            cur = int(data.get("bank_tier", 0))
            if cur >= max_bank_tier():
                return False, _t(lang, "top_tier_title"), _t(lang, "top_tier_body")

            data["bank_tier"] = cur + 1
            msg_text = _t(
                lang, "fx_bank_tier",
                tier=bank_name(data["bank_tier"]),
                cap=f"{bank_cap(data['bank_tier']):,}",
                rate=f"{int(bank_rate(data['bank_tier'])*100*10)/10}",
            )
        elif effect == "coin_booster":
            effects["coin_booster"] = 1
            msg_text = _t(lang, "fx_coin")
        elif effect == "streak_insurance":
            effects["streak_insurance"] = 1
            msg_text = _t(lang, "fx_streak")
        elif effect == "gambling_boost":
            effects["gambling_boost"] = 1
            msg_text = _t(lang, "fx_gamble")
        elif effect == "work_boost":
            effects["work_boost"] = 1
            msg_text = _t(lang, "fx_work_boost")
        else:
            return False, _t(lang, "no_effect_title"), _t(lang, "no_effect_body")

        return True, _t(lang, "used_title", emoji=item["emoji"], name=item["name"]), msg_text

    @commands.hybrid_command(
        name="use",
        description=CMDS.text("use.description"),
        help=CMDS.help("use"),
    )
    async def use(self, ctx: commands.Context, item_id: str = None):
        lang = get_lang(ctx)

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        # With an item id, resolve it directly; without one, open the picker panel
        if item_id:
            iid  = item_id.lower()
            data = await self.get_user_economy_data(ctx.author.id)
            applied, title, body = self._use_item_effect(data, iid, get_item(iid), lang)
            if applied:
                _consume_one(data, iid)
                await self.save_user_economy_data(ctx.author.id)
            view = _info_view(title, body)
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        panel = await _UseItemView.create(self, ctx.author.id, lang)
        if panel is None:
            view = _info_view(_t(lang, "nothing_use_title"), _t(lang, "nothing_use_cmd"))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)
        if ctx.interaction:
            return await ctx.interaction.followup.send(view=panel, ephemeral=True)
        return await ctx.send(view=panel)

    @commands.hybrid_command(
        name="inventory", aliases=["inv", "bag"],
        description=CMDS.text("inventory.description"),
        help=CMDS.help("inventory"),
    )
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        lang = get_lang(ctx)

        # Defer the interaction to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        target = member or ctx.author
        data   = await self.get_user_economy_data(target.id)
        inv    = data.get("inventory", {})
        if not inv:
            view = _info_view(_t(lang, "empty_bag_title"), _t(lang, "empty_bag_body"))
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view)
            return await ctx.send(view=view)

        message = await self._show_loading_card(ctx, "inventory")

        # Fetch avatar for the card
        avatar_url = str(getattr(target.display_avatar, "url", "")) or None
        avatar_bytes = await fetch_avatar_bytes(avatar_url)

        # Build sections grouped by category
        groups: dict[str, list[dict]] = {"consumable": [], "upgrade": [], "collectible": [], "other": []}
        for iid, count in sorted(inv.items()):
            item = get_item(iid)
            if not item:
                groups["other"].append({"emoji": "📦", "name": iid, "count": int(count), "desc": ""})
                continue
            groups[item["category"]].append({
                "emoji": str(item.get("emoji", "📦")),
                "name": str(item["name"]),
                "count": int(count),
                "desc": str(item.get("description", "")),
            })
        labels = {
            "consumable": _t(lang, "cat_consumable"),
            "upgrade": _t(lang, "cat_upgrade"),
            "collectible": _t(lang, "cat_collectible"),
            "other": _t(lang, "cat_misc"),
        }
        sections = [
            {"label": labels[cat], "items": items}
            for cat, items in groups.items()
            if items
        ]

        card = await render_inventory_card(
            avatar_bytes=avatar_bytes,
            name=target.display_name,
            balance=int(data.get("balance", 0)),
            sections=sections,
        )
        view = _card_view(_t(lang, "bag_title", name=target.display_name), "inventory.png", [])
        await message.edit(view=view, attachments=[discord.File(card, "inventory.png")])
