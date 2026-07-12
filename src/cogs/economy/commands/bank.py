"""
Economy — bank commands (deposit, withdraw, upgrade).
"""
from discord.ext import commands
from ..data import (
    _info_view, _check_achievements, _log_tx, get_emoji,
    BANK_TIERS, bank_info, bank_cap, bank_name, bank_rate, max_bank_tier,
)


class BankMixin:
    """bank group commands."""

    @commands.hybrid_group(name="bank",
                           description="Manage your café vault: deposit, withdraw, upgrade",
                           help="{ 'en': 'manage your café vault 🏦', 'de': 'verwalte deinen Tresor', 'es': 'gestiona tu bóveda 🏦' }",
                           invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        tier = int(data.get("bank_tier", 0))
        cap  = bank_cap(tier)
        rate = bank_rate(tier)
        body = (
            f"**{bank_name(tier)}** — tier **{tier+1}/{len(BANK_TIERS)}**\n"
            f"• Stored: **{int(data['bank']):,}** / **{cap:,}** 🏦\n"
            f"• Daily interest: **{rate*100:.2f}%** (auto-credited every 24h)\n\n"
            f"-# Use `bank deposit`, `bank withdraw` or `bank upgrade` to manage."
        )
        await ctx.send(view=_info_view("🏦 Your Vault", body))

    @bank.command(name="deposit", description="Move cash from wallet into the vault")
    async def bank_deposit(self, ctx: commands.Context, amount: str):
        data = self.get_user_economy_data(ctx.author.id)
        cap  = bank_cap(int(data.get("bank_tier", 0)))
        free = max(0, cap - int(data["bank"]))

        if amount.lower() == "all":
            amt = min(int(data["balance"]), free)
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Use a number or `all`."))

        if amt <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Nothing to deposit", "Either your wallet is empty or your vault is full."))
        if amt > data["balance"]:
            return await ctx.send(view=_info_view("💸 Not enough cash", "Your pastry bag doesn't have that much."))
        if amt > free:
            return await ctx.send(view=_info_view(
                "🏦 Vault full",
                f"You can store at most **{free:,}** more 🥐 in a **{bank_name(data['bank_tier'])}**.\n-# Upgrade with `bank upgrade`.",
            ))

        data["balance"] -= amt
        data["bank"]    += amt
        _log_tx(data, "deposit", amt, "wallet → vault")
        _check_achievements(data)
        self.save_economy_data()
        await ctx.send(view=_info_view("🏦 Deposited", f"Stored **{amt:,}** 🥐 in your vault.\n-# Vault: **{data['bank']:,}** / **{cap:,}**"))

    @bank.command(name="withdraw", description="Move coins from the vault back to your wallet")
    async def bank_withdraw(self, ctx: commands.Context, amount: str):
        data = self.get_user_economy_data(ctx.author.id)
        if amount.lower() == "all":
            amt = int(data["bank"])
        else:
            try:
                amt = int(amount)
            except ValueError:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Use a number or `all`."))

        if amt <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Nothing to withdraw", "Your vault is empty."))
        if amt > data["bank"]:
            return await ctx.send(view=_info_view("🏦 Not enough", "You don't have that much stored."))

        data["bank"]    -= amt
        data["balance"] += amt
        _log_tx(data, "withdraw", amt, "vault → wallet")
        self.save_economy_data()
        await ctx.send(view=_info_view("🥐 Withdrawn", f"Took **{amt:,}** 🥐 from your vault.\n-# Wallet: **{data['balance']:,}** 🥐"))

    @bank.command(name="upgrade", description="Pay to upgrade your vault to the next tier")
    async def bank_upgrade(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        cur  = int(data.get("bank_tier", 0))
        if cur >= max_bank_tier():
            return await ctx.send(view=_info_view("🏆 Maxed out", "Your vault is already a **Diamond Vault** — the highest tier."))
        next_tier = cur + 1
        cost = bank_cap(next_tier) // 2
        if data["balance"] + data["bank"] < cost:
            return await ctx.send(view=_info_view(
                "💸 Not enough net worth",
                f"Upgrading to **{bank_name(next_tier)}** costs **{cost:,}** 🥐 (paid from wallet first, then vault).",
            ))
        from_wallet = min(int(data["balance"]), cost)
        from_bank   = cost - from_wallet
        data["balance"] -= from_wallet
        data["bank"]    -= from_bank
        data["bank_tier"] = next_tier
        _log_tx(data, "upgrade", -cost, f"vault → {bank_name(next_tier)}")
        self.save_economy_data()
        await ctx.send(view=_info_view(
            "🏦 Vault upgraded",
            f"Welcome to your shiny new **{bank_name(next_tier)}**!\n"
            f"• New cap: **{bank_cap(next_tier):,}** 🥐\n"
            f"• Daily interest: **{bank_rate(next_tier)*100:.2f}%**",
        ))
