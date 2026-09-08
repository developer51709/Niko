"""
Economy — shop commands (shop, buy, sell, use, inventory).
"""
import discord
from discord.ext import commands
from ..data import (
    _info_view, _card_view, _check_achievements,
    SHOP_ITEMS, get_item, get_emoji,
    add_xp, bank_name, bank_cap, bank_rate, max_bank_tier,
)
from utils.image.economy_card import render_shop_card, render_inventory_card, fetch_avatar_bytes


class _ShopActionView(discord.ui.LayoutView):
    """Shop card controls; the buttons open user-only transaction panels."""

    def __init__(self, cog, *, timeout: float | None = 900, image_name: str = "shop.png"):
        super().__init__(timeout=timeout)
        self.cog = cog
        container = discord.ui.Container(
            discord.ui.MediaGallery(discord.MediaGalleryItem(media=f"attachment://{image_name}")),
            discord.ui.TextDisplay(content="-# Choose an action below to open a private checkout panel."),
            discord.ui.ActionRow(
                discord.ui.Button(label="Buy", style=discord.ButtonStyle.success, custom_id="economy:shop:buy"),
                discord.ui.Button(label="Sell", style=discord.ButtonStyle.secondary, custom_id="economy:shop:sell"),
            ),
            accent_colour=discord.Colour(0xC8853F),
        )
        action_row = container.children[2]
        action_row.children[0].callback = self._buy
        action_row.children[1].callback = self._sell
        self.add_item(container)

    async def _buy(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=await _ShopTransactionView.create(self.cog, "buy", interaction.user.id), ephemeral=True)

    async def _sell(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=await _ShopTransactionView.create(self.cog, "sell", interaction.user.id), ephemeral=True)


class _ShopTransactionView(discord.ui.LayoutView):
    """Two-step private checkout: item first, then quantity."""

    def __init__(self, cog, mode: str, user_id: int, item_options: list[discord.SelectOption]):
        super().__init__(timeout=300)
        self.cog = cog
        self.mode = mode
        self.user_id = user_id
        self.item_id: str | None = None
        self.amount = 1
        self.amount_select = discord.ui.Select(
            placeholder="2. Choose an amount",
            options=[discord.SelectOption(label="Choose an item first", value="1")],
            disabled=True,
        )
        self.item_select = discord.ui.Select(
            placeholder=f"1. Select an item to {mode}", options=item_options,
        )
        self.item_select.callback = self._item_changed
        self.amount_select.callback = self._amount_changed
        confirm = discord.ui.Button(
            label="Confirm purchase" if mode == "buy" else "Confirm sale",
            style=discord.ButtonStyle.success if mode == "buy" else discord.ButtonStyle.primary,
        )
        confirm.callback = self._confirm
        container = discord.ui.Container(
            discord.ui.TextDisplay(content=f"### {'🛍️ Buy from' if mode == 'buy' else '💰 Sell from'} the boutique\n-# Select an item, then choose how many you want."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.ActionRow(self.item_select),
            discord.ui.ActionRow(self.amount_select),
            discord.ui.ActionRow(confirm),
            accent_colour=discord.Colour(0x57F287 if mode == "buy" else 0x5865F2),
        )
        self.add_item(container)

    @classmethod
    async def create(cls, cog, mode: str, user_id: int):
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
            detail = f"{item['price']:,} coins" if mode == "buy" else f"{count} owned · {int(item.get('sell', item['price'] // 3)):,} each"
            options.append(discord.SelectOption(
                label=str(item["name"])[:100], value=str(iid), description=detail[:100], emoji=str(item.get("emoji", "📦")),
            ))
        if not options:
            options = [discord.SelectOption(label="Your inventory is empty", value="__empty", description="Buy something first")]
        return cls(cog, mode, user_id, options[:25])

    async def _item_changed(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This private panel belongs to someone else.", ephemeral=True)
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
            return await interaction.response.send_message("This private panel belongs to someone else.", ephemeral=True)
        self.amount = int(self.amount_select.values[0])
        await interaction.response.edit_message(view=self)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This private panel belongs to someone else.", ephemeral=True)
        if not self.item_id or self.item_id == "__empty":
            return await interaction.response.send_message("Select an item first.", ephemeral=True)
        await interaction.response.defer()
        await self.cog._complete_shop_transaction(interaction, self.mode, self.item_id, self.amount)


class ShopMixin:
    """shop, buy, sell, use, inventory commands."""

    async def _complete_shop_transaction(self, interaction: discord.Interaction, mode: str, item_id: str, count: int):
        """Validate and commit a transaction selected through the private panel."""
        item = get_item(item_id)
        if not item or count < 1:
            return await interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Invalid selection", "That item or amount is no longer available."), ephemeral=True)
        data = await self.get_user_economy_data(interaction.user.id)
        iid = item_id.lower()
        if int(data.get("level", 0)) < int(item.get("min_level", 0)):
            return await interaction.followup.send(view=_info_view("🔒 Locked", f"**{item['name']}** requires career level **{item['min_level']}**."), ephemeral=True)
        if mode == "buy":
            total = int(item["price"]) * count
            if int(data.get("balance", 0)) < total:
                return await interaction.followup.send(view=_info_view("💸 Not enough cash", f"You need **{total:,}** 🥐 but only have **{data['balance']:,}**."), ephemeral=True)
            self._credit(data, -total, "buy", f"{count}x {item['name']}")
            data.setdefault("inventory", {})[iid] = int(data["inventory"].get(iid, 0)) + count
            title = "🛍️ Purchase complete"
            message = f"You bought **{count}x {item['emoji']} {item['name']}** for **{total:,}** 🥐.\\n-# New balance: **{data['balance']:,}** 🥐"
        else:
            have = int(data.setdefault("inventory", {}).get(iid, 0))
            if have < count:
                return await interaction.followup.send(view=_info_view("📦 Not enough", f"You only have **{have}** of those."), ephemeral=True)
            gain = int(item.get("sell", item["price"] // 3)) * count
            self._credit(data, gain, "sell", f"{count}x {item['name']}")
            data["inventory"][iid] = have - count
            if data["inventory"][iid] <= 0:
                del data["inventory"][iid]
            title = "💰 Sold"
            message = f"You sold **{count}x {item['emoji']} {item['name']}** for **{gain:,}** 🥐.\\n-# New balance: **{data['balance']:,}** 🥐"
        _check_achievements(data)
        await self.save_user_economy_data(interaction.user.id)
        await interaction.followup.send(view=_info_view(title, message), ephemeral=True)

    @commands.hybrid_command(
        name="shop",
        description="Browse the café boutique",
        help="{ 'en': 'browse the café boutique 🛍️✨', 'de': 'stöbere in der Boutique', 'es': 'explora la boutique 🛍️✨' }",
    )
    async def shop(self, ctx: commands.Context, category: str = None):
        cats = ("consumable", "upgrade", "collectible")
        if ctx.interaction:
            await ctx.interaction.response.defer()
        if category and category.lower() not in cats:
            view = _info_view("❌ Unknown category", f"Try one of: {', '.join('`' + c + '`' for c in cats)}")
            return await (ctx.interaction.followup.send(view=view) if ctx.interaction else ctx.send(view=view))
        cat_filter = category.lower() if category else None
        data = await self.get_user_economy_data(ctx.author.id)
        items = [dict(item, item_id=iid) for iid, item in SHOP_ITEMS.items() if not cat_filter or item["category"] == cat_filter]
        if not items:
            view = _info_view("☕ Empty shelves", "Nothing in stock for that category.")
        else:
            card = await render_shop_card(items=items, balance=int(data.get("balance", 0)), category=cat_filter)
            view = _ShopActionView(self, image_name="shop.png")
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=view, file=discord.File(card, "shop.png"))
            return await ctx.send(view=view, file=discord.File(card, "shop.png"))
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view)
        else:
            await ctx.send(view=view)

    async def buy(self, ctx: commands.Context, item_id: str, count: int = 1):

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        # Ensure the amount is a positive number
        if count <= 0:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))

        # Check if the item exists
        item = get_item(item_id)
        if not item:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Out of stock", f"No item called `{item_id}`."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Out of stock", f"No item called `{item_id}`."))

        # Check if the user meets the level requirements
        data = await self.get_user_economy_data(ctx.author.id)
        if data["level"] < item.get("min_level", 0):
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('vm_lock')} Locked", f"**{item['name']}** requires career level **{item['min_level']}**."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('vm_lock')} Locked", f"**{item['name']}** requires career level **{item['min_level']}**."))

        # Check if the user has enough balance to buy the item
        total = item["price"] * count
        if data["balance"] < total:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("💸 Not enough cash", f"You need **{total:,}** 🥐 (you have **{data['balance']:,}**)."))
            else:
                return await ctx.send(view=_info_view("💸 Not enough cash", f"You need **{total:,}** 🥐 (you have **{data['balance']:,}**)."))

        self._credit(data, -total, "buy", f"{count}x {item['name']}")
        inv = data["inventory"]
        inv[item_id.lower()] = int(inv.get(item_id.lower(), 0)) + count
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(
                "🛍️ Purchase complete",
                f"You bought **{count}x {item['emoji']} {item['name']}** for **{total:,}** 🥐.\n"
                f"-# New balance: **{data['balance']:,}** 🥐",
            ))
        else:
            await ctx.send(view=_info_view(
                "🛍️ Purchase complete",
                f"You bought **{count}x {item['emoji']} {item['name']}** for **{total:,}** 🥐.\n"
                f"-# New balance: **{data['balance']:,}** 🥐",
            ))

    async def sell(self, ctx: commands.Context, item_id: str, count: int = 1):

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        # Verify the user provided a positive amount
        if count <= 0:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))

        # Verify the item exists
        iid  = item_id.lower()
        item = get_item(iid)
        if not item:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))

        # Ensure the user has enough to sell
        data = await self.get_user_economy_data(ctx.author.id)
        have = int(data["inventory"].get(iid, 0))
        if have < count:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("📦 Not enough", f"You only have **{have}** of those."))
            else:
                return await ctx.send(view=_info_view("📦 Not enough", f"You only have **{have}** of those."))

        gain = int(item.get("sell", item["price"] // 3)) * count
        self._credit(data, gain, "sell", f"{count}x {item['name']}")
        data["inventory"][iid] = have - count
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        await self.save_user_economy_data(ctx.author.id)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(
                "💰 Sold",
                f"You sold **{count}x {item['emoji']} {item['name']}** for **{gain:,}** 🥐.\n"
                f"-# New balance: **{data['balance']:,}** 🥐",
            ))
        else:
            await ctx.send(view=_info_view(
                "💰 Sold",
                f"You sold **{count}x {item['emoji']} {item['name']}** for **{gain:,}** 🥐.\n"
                f"-# New balance: **{data['balance']:,}** 🥐",
            ))

    @commands.hybrid_command(
        name="use",
        description="Use a consumable or upgrade item",
        help="{ 'en': 'use a consumable from your bag 🧪', 'de': 'benutze ein Item aus deinem Bag', 'es': 'usa un objeto de tu inventario 🧪' }"
    )
    async def use(self, ctx: commands.Context, item_id: str):

        # Defer slash interactions to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        iid  = item_id.lower()
        item = get_item(iid)
        if not item:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))

        data = await self.get_user_economy_data(ctx.author.id)
        if int(data["inventory"].get(iid, 0)) < 1:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("📦 None in bag", f"You don't have any **{item['name']}**."))
            else:
                return await ctx.send(view=_info_view("📦 None in bag", f"You don't have any **{item['name']}**."))

        if item["category"] == "collectible":
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("🎖️ Collectible", "Collectibles can't be used — they're for showing off on your profile."))
            else:
                return await ctx.send(view=_info_view("🎖️ Collectible", "Collectibles can't be used — they're for showing off on your profile."))

        effect   = item.get("effect")
        msg_text = ""
        effects  = data.setdefault("effects", {})

        if effect == "work_cooldown_half":
            effects["work_cooldown_half"] = True
            msg_text = "Your next work cooldown will be cut in half. ☕✨"
        elif effect == "crime_boost":
            effects["crime_boost"] = 1
            msg_text = "Your next crime gets +25% success. 🔓"
        elif effect == "rob_shield":
            effects["rob_shield"] = 1
            msg_text = "The next robbery against you will be blocked. 🛡️"
        elif effect == "lottery_boost":
            effects["lottery_boost"] = 1
            msg_text = "Your next lottery purchase counts double. 🍀"
        elif effect == "xp_potion":
            new_lvl, _, leveled = add_xp(data, 75)
            msg_text = f"+75 XP. " + (f"You leveled up to **{new_lvl}**! ✨" if leveled else "")
        elif effect == "bank_tier_up":
            cur = int(data.get("bank_tier", 0))
            if cur >= max_bank_tier():
                if ctx.interaction:
                    return await ctx.interaction.followup.send(view=_info_view("🏦 Already top tier", "Your vault is already a Diamond Vault — the best of the best."))
                else:
                    return await ctx.send(view=_info_view("🏦 Already top tier", "Your vault is already a Diamond Vault — the best of the best."))

            data["bank_tier"] = cur + 1
            msg_text = (
                f"Your vault is now a **{bank_name(data['bank_tier'])}** with cap "
                f"**{bank_cap(data['bank_tier']):,}** and "
                f"**{int(bank_rate(data['bank_tier'])*100*10)/10}%** daily interest. 🏦✨"
            )
        elif effect == "coin_booster":
            effects["coin_booster"] = 1
            msg_text = "Your next coinflip gets 60/40 odds in your favor. 🪙✨"
        elif effect == "streak_insurance":
            effects["streak_insurance"] = 1
            msg_text = "Your daily streak is now protected for one missed day. 🛡️🔥"
        elif effect == "gambling_boost":
            effects["gambling_boost"] = 1
            msg_text = "Your next gambling win will pay 1.5x the normal amount! 🎰✨"
        elif effect == "work_boost":
            effects["work_boost"] = 1
            msg_text = "Your next work shift will pay +10% extra. 🧲✨"
        else:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("🤔 No effect", "This item doesn't seem to do anything right now."))
            else:
                return await ctx.send(view=_info_view("🤔 No effect", "This item doesn't seem to do anything right now."))

        data["inventory"][iid] = int(data["inventory"][iid]) - 1
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        await self.save_user_economy_data(ctx.author.id)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(f"{item['emoji']} {item['name']} used", msg_text))
        else:
            await ctx.send(view=_info_view(f"{item['emoji']} {item['name']} used", msg_text))

    @commands.hybrid_command(
        name="inventory", aliases=["inv", "bag"],
        description="View your inventory grouped by category",
        help="{ 'en': 'check your collection of treats 🎒✨', 'de': 'sieh dir deinen Bag an', 'es': 'revisa tu inventario 🎒✨' }"
    )
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):

        # Defer the interaction to avoid interaction errors
        if ctx.interaction:
            await ctx.interaction.response.defer()

        target = member or ctx.author
        data   = await self.get_user_economy_data(target.id)
        inv    = data.get("inventory", {})
        if not inv:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view("🎒 Empty bag", "Nothing here yet — try the `shop`!"))
            else:
                return await ctx.send(view=_info_view("🎒 Empty bag", "Nothing here yet — try the `shop`!"))

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
            "consumable": "🧪 Consumables",
            "upgrade": "🏦 Upgrades",
            "collectible": "🎖️ Collectibles",
            "other": "📦 Misc",
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
        view = _card_view(f"🎒 {target.display_name}'s Bag", "inventory.png", [])
        if ctx.interaction:
            await ctx.interaction.followup.send(view=view, file=discord.File(card, "inventory.png"))
        else:
            await ctx.send(view=view, file=discord.File(card, "inventory.png"))
