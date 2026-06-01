"""
Economy — shop commands (shop, buy, sell, use, inventory).
"""
import discord
from discord.ext import commands
from ..data import (
    _info_view, _check_achievements, _resolve_prefix,
    SHOP_ITEMS, get_item, get_emoji,
    add_xp, bank_name, bank_cap, bank_rate, max_bank_tier,
)


class ShopMixin:
    """shop, buy, sell, use, inventory commands."""

    @commands.hybrid_command(name="shop",
                             description="Browse the café boutique",
                             help="{ 'en': 'browse the café boutique 🛍️✨', 'de': 'stöbere in der Boutique', 'es': 'explora la boutique 🛍️✨' }")
    async def shop(self, ctx: commands.Context, category: str = None):
        prefix = await _resolve_prefix(self.bot, ctx)
        cats = ("consumable", "upgrade", "collectible")
        if category and category.lower() not in cats:
            return await ctx.send(view=_info_view(
                f"{get_emoji('icon_cross')} Unknown category",
                f"Try one of: {', '.join('`' + c + '`' for c in cats)}"
            ))
        cat_filter = category.lower() if category else None
        sections: dict[str, list[str]] = {c: [] for c in cats}
        data = self.get_user_economy_data(ctx.author.id)
        lvl  = int(data.get("level", 0))
        for iid, item in SHOP_ITEMS.items():
            if cat_filter and item["category"] != cat_filter:
                continue
            lock = "" if lvl >= item.get("min_level", 0) else f"  {get_emoji('icon_lock')} lvl {item['min_level']}"
            sections[item["category"]].append(
                f"{item['emoji']} **{item['name']}** `({iid})` — **{item['price']:,}** 🥐{lock}\n"
                f"-# *{item['description']}*"
            )
        body_blocks = []
        labels = {"consumable": "Consumables", "upgrade": "Upgrades", "collectible": "Collectibles"}
        for c in cats:
            if sections[c]:
                body_blocks.append(f"### **{labels[c]}**\n" + "\n\n".join(sections[c]))
        if not body_blocks:
            return await ctx.send(view=_info_view("☕ Empty shelves", "Nothing in stock for that category."))
        body = "\n\n".join(body_blocks) + f"\n\n-# Buy with `{prefix}buy <id> [count]`. Use with `{prefix}use <id>`."
        await ctx.send(view=_info_view("🛍️ Niko's Café Boutique", body))

    @commands.hybrid_command(name="buy",
                             description="Buy an item from the shop",
                             help="{ 'en': 'buy a treat from the shop 🍰✨', 'de': 'kauf etwas im Shop', 'es': 'compra algo en la tienda 🍰✨' }")
    async def buy(self, ctx: commands.Context, item_id: str, count: int = 1):
        if count <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
        item = get_item(item_id)
        if not item:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Out of stock", f"No item called `{item_id}`."))
        data = self.get_user_economy_data(ctx.author.id)
        if data["level"] < item.get("min_level", 0):
            return await ctx.send(view=_info_view(f"{get_emoji('vm_lock')} Locked", f"**{item['name']}** requires career level **{item['min_level']}**."))
        total = item["price"] * count
        if data["balance"] < total:
            return await ctx.send(view=_info_view("💸 Not enough cash", f"You need **{total:,}** 🥐 (you have **{data['balance']:,}**)."))
        self._credit(data, -total, "buy", f"{count}x {item['name']}")
        inv = data["inventory"]
        inv[item_id.lower()] = int(inv.get(item_id.lower(), 0)) + count
        _check_achievements(data)
        self.save_economy_data()
        await ctx.send(view=_info_view(
            "🛍️ Purchase complete",
            f"You bought **{count}x {item['emoji']} {item['name']}** for **{total:,}** 🥐.\n"
            f"-# New balance: **{data['balance']:,}** 🥐",
        ))

    @commands.hybrid_command(name="sell",
                             description="Sell an item back from your inventory",
                             help="{ 'en': 'sell a treat back for some coins 💰', 'de': 'verkauf etwas aus deinem Bag', 'es': 'vende algo de tu inventario 💰' }")
    async def sell(self, ctx: commands.Context, item_id: str, count: int = 1):
        if count <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
        iid  = item_id.lower()
        item = get_item(iid)
        if not item:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))
        data = self.get_user_economy_data(ctx.author.id)
        have = int(data["inventory"].get(iid, 0))
        if have < count:
            return await ctx.send(view=_info_view("📦 Not enough", f"You only have **{have}** of those."))
        gain = int(item.get("sell", item["price"] // 3)) * count
        self._credit(data, gain, "sell", f"{count}x {item['name']}")
        data["inventory"][iid] = have - count
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        self.save_economy_data()
        await ctx.send(view=_info_view(
            "💰 Sold",
            f"You sold **{count}x {item['emoji']} {item['name']}** for **{gain:,}** 🥐.\n"
            f"-# New balance: **{data['balance']:,}** 🥐",
        ))

    @commands.hybrid_command(name="use",
                             description="Use a consumable or upgrade item",
                             help="{ 'en': 'use a consumable from your bag 🧪', 'de': 'benutze ein Item aus deinem Bag', 'es': 'usa un objeto de tu inventario 🧪' }")
    async def use(self, ctx: commands.Context, item_id: str):
        iid  = item_id.lower()
        item = get_item(iid)
        if not item:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))
        data = self.get_user_economy_data(ctx.author.id)
        if int(data["inventory"].get(iid, 0)) < 1:
            return await ctx.send(view=_info_view("📦 None in bag", f"You don't have any **{item['name']}**."))
        if item["category"] == "collectible":
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
                return await ctx.send(view=_info_view("🏦 Already top tier", "Your vault is already a Diamond Vault — the best of the best."))
            data["bank_tier"] = cur + 1
            msg_text = (
                f"Your vault is now a **{bank_name(data['bank_tier'])}** with cap "
                f"**{bank_cap(data['bank_tier']):,}** and "
                f"**{int(bank_rate(data['bank_tier'])*100*10)/10}%** daily interest. 🏦✨"
            )
        else:
            return await ctx.send(view=_info_view("🤔 No effect", "This item doesn't seem to do anything right now."))

        data["inventory"][iid] = int(data["inventory"][iid]) - 1
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        self.save_economy_data()
        await ctx.send(view=_info_view(f"{item['emoji']} {item['name']} used", msg_text))

    @commands.hybrid_command(name="inventory", aliases=["inv", "bag"],
                             description="View your inventory grouped by category",
                             help="{ 'en': 'check your collection of treats 🎒✨', 'de': 'sieh dir deinen Bag an', 'es': 'revisa tu inventario 🎒✨' }")
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        data   = self.get_user_economy_data(target.id)
        inv    = data.get("inventory", {})
        if not inv:
            return await ctx.send(view=_info_view("🎒 Empty bag", "Nothing here yet — try the `shop`!"))
        groups = {"consumable": [], "upgrade": [], "collectible": [], "other": []}
        for iid, count in sorted(inv.items()):
            item = get_item(iid)
            if not item:
                groups["other"].append(f"• `{iid}` × **{count}**")
                continue
            groups[item["category"]].append(f"{item['emoji']} **{item['name']}** × **{count}**  -# *{item['description']}*")
        labels = {"consumable": "🧪 Consumables", "upgrade": "🏦 Upgrades", "collectible": "🎖️ Collectibles", "other": "📦 Misc"}
        body_parts = []
        for cat, items in groups.items():
            if items:
                body_parts.append(f"**{labels[cat]}**\n" + "\n".join(items))
        body = "\n\n".join(body_parts)
        await ctx.send(view=_info_view(f"🎒 {target.display_name}'s Bag", body))
