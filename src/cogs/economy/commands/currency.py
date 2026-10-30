"""
Economy — currency commands: balance, profile, daily, work, pay, transactions, networth.
"""
import discord
from discord.ext import commands
from ..data import (
    msg, _info_view, _card_view, _reply, _fmt_remaining, locale_t,
    _check_achievements, _resolve_prefix,
    COOLDOWN_DAILY, COOLDOWN_WORK,
    get_job, get_emoji,
    total_xp_for_level, xp_to_next, bank_name,
    add_xp,
    ACCENT_GOLD, ACCENT_GREEN,
)
from ..voting import vote_earnings_multiplier
import random
import datetime

from utils.i18n import get_lang
from utils.locales import load_locales
from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "currency"))


class CurrencyMixin:
    """balance, profile, daily, work, pay, transactions, networth."""

    # ── balance / profile ────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="balance", aliases=["bal", "wallet"],
        description=CMDS.text("balance.description"),
        help=CMDS.help("balance"),
    )
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        target = member or ctx.author
        await self._send_balance_card(ctx, target, title=T(get_lang(ctx), "wallet_title"))

    @commands.hybrid_command(
        name="profile", aliases=["prof", "stats"],
        description=CMDS.text("profile.description"),
        help=CMDS.help("profile"),
    )
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        from ..data import ACHIEVEMENTS, achievement_icon, achievement_name
        lang = get_lang(ctx)
        target = member or ctx.author
        await self._send_balance_card(ctx, target, title=T(lang, "profile_title"))
        data = await self.get_user_economy_data(target.id)
        ach = data.get("achievements", [])
        ach_line = (
            ", ".join(
                f"{achievement_icon(ACHIEVEMENTS[a])} {achievement_name(a, ACHIEVEMENTS[a], lang)}"
                for a in ach if a in ACHIEVEMENTS
            )
            or T(lang, "no_badges")
        )
        txs = data.get("transactions", [])[:5]
        if txs:
            lines = []
            for t in txs:
                sign = "+" if t["amount"] >= 0 else "−"
                lines.append(f"`{t['kind'][:10]:<10}` {sign}{abs(t['amount']):,}  ·  {t.get('note','')}")
            tx_block = "\n".join(lines)
        else:
            tx_block = T(lang, "no_tx")
        view = _info_view(
            T(lang, "extras_title", name=target.display_name),
            T(lang, "extras_body", badges=ach_line, activity=tx_block),
        )
        await _reply(ctx, view, allowed_mentions=discord.AllowedMentions.none())

    # ── daily ────────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="daily",
        description=CMDS.text("daily.description"),
        help=CMDS.help("daily"),
    )
    async def daily(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        elapsed = now - int(data.get("last_daily", 0))

        if elapsed < COOLDOWN_DAILY:
            remain = COOLDOWN_DAILY - elapsed
            return await _reply(ctx, _info_view(
                T(lang, "daily_cd_title"),
                T(lang, "daily_cd_body", time=_fmt_remaining(remain)),
            ))

        streak = int(data.get("daily_streak", 0))
        effects = data.setdefault("effects", {})
        if elapsed > 2 * COOLDOWN_DAILY:
            # Streak insurance: if user missed exactly one day, protect the streak
            if streak >= 3 and effects.pop("streak_insurance", 0):
                streak += 1  # streak preserved, just count as consecutive
            else:
                streak = 1
        else:
            streak += 1
        multiplier = 1 + min(streak, 7) * 0.2
        base = 1000
        # Top.gg votes keep paying forward: while a vote streak is alive it also
        # tops up every daily claim and every shift (see cogs/economy/voting.py).
        vote_bonus = vote_earnings_multiplier(data.get("vote_streak", 0))
        reward = int(base * multiplier * vote_bonus)

        # ── Streak milestone bonuses ──
        STREAK_MILESTONES = {
            7:  (500,   ["xp_potion"]),
            14: (1500,  ["lucky_charm"]),
            30: (5000,  ["espresso_shot", "lockpick"]),
            60: (15000, ["rob_shield", "lucky_charm"]),
            90: (50000, ["espresso_shot", "lockpick", "rob_shield", "lucky_charm", "xp_potion"]),
        }
        milestone_bonus = 0
        milestone_items = []
        if streak in STREAK_MILESTONES:
            ms_bonus, ms_items = STREAK_MILESTONES[streak]
            milestone_bonus = ms_bonus
            milestone_items = ms_items
            inv = data.setdefault("inventory", {})
            for item_id in ms_items:
                inv[item_id] = int(inv.get(item_id, 0)) + 1

        total_reward = reward + milestone_bonus
        self._credit(data, total_reward, "daily",
                     T(lang, "note_daily", streak=streak, mult=f"{multiplier:.1f}"))
        data["daily_streak"] = streak
        data["last_daily"] = now
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)

        subtitle = T(lang, "daily_subtitle", streak=streak, mult=f"{multiplier:.1f}")
        if vote_bonus > 1:
            subtitle += T(lang, "vote_bonus", bonus=f"{vote_bonus:.2f}")
        footer = msg(ctx, "daily_success", reward=total_reward)
        if milestone_items:
            from ..data import get_item
            item_names = ", ".join(
                get_item(iid)["name"] for iid in milestone_items if get_item(iid)
            )
            footer += T(lang, "milestone", items=item_names, bonus=f"{milestone_bonus:,}")

        await self._send_reward_card(
            ctx,
            title=T(lang, "daily_title"),
            subtitle=subtitle,
            amount=total_reward,
            accent=ACCENT_GOLD,
            footer=footer,
        )

    # ── work ─────────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="work",
        description=CMDS.text("work.description"),
        help=CMDS.help("work"),
    )
    async def work(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        import time
        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        job = get_job(data.get("job"))
        cd = int(job.get("cooldown", COOLDOWN_WORK))

        effects = data.setdefault("effects", {})
        if effects.get("work_cooldown_half"):
            cd = cd // 2

        elapsed = now - int(data.get("last_work", 0))
        if elapsed < cd:
            return await _reply(ctx, _info_view(
                T(lang, "work_cd_title"),
                T(lang, "work_cd_body", time=_fmt_remaining(cd - elapsed)),
            ))

        if effects.get("work_cooldown_half"):
            effects.pop("work_cooldown_half", None)

        reward = random.randint(int(job["min_pay"]), int(job["max_pay"]))
        if effects.pop("work_boost", 0):
            reward = int(reward * 1.10)
        vote_bonus = vote_earnings_multiplier(data.get("vote_streak", 0))
        if vote_bonus > 1:
            reward = int(reward * vote_bonus)
        self._credit(data, reward, "work", T(lang, "note_work", job=job["name"]))
        data["last_work"] = now
        data["times_worked"] = int(data.get("times_worked", 0)) + 1

        new_lvl, gained_levels, leveled = add_xp(data, int(job.get("xp_per_shift", 10)))
        announce = msg(ctx, "level_up", level=new_lvl) if leveled else None

        newly = _check_achievements(data, lang=lang)
        await self.save_user_economy_data(ctx.author.id)

        subtitle = T(
            lang, "work_subtitle",
            emoji=job["emoji"], job=job["name"], xp=job.get("xp_per_shift", 10),
        )
        if vote_bonus > 1:
            subtitle += T(lang, "vote_bonus", bonus=f"{vote_bonus:.2f}")
        footer = msg(ctx, "work_success", reward=reward)
        if newly:
            footer += T(lang, "unlocked", items=", ".join(newly))

        await self._send_reward_card(
            ctx, title=T(lang, "work_title"), subtitle=subtitle, amount=reward,
            accent=ACCENT_GREEN, footer=footer, announce=announce,
        )

    # ── pay ───────────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="pay", aliases=["give"],
        description=CMDS.text("pay.description"),
        help=CMDS.help("pay"),
    )
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        if not member or member.bot or member.id == ctx.author.id:
            return await _reply(ctx, _info_view(
                T(lang, "bad_target_title"), T(lang, "bad_target_body")))

        if amount <= 0:
            return await _reply(ctx, _info_view(
                T(lang, "bad_amount_title"), T(lang, "bad_amount_body")))

        data   = await self.get_user_economy_data(ctx.author.id)
        target = await self.get_user_economy_data(member.id)
        if data["balance"] < amount:
            return await _reply(ctx, _info_view(
                T(lang, "no_cash_title"), T(lang, "no_cash_body")))

        self._credit(data, -amount, "pay", T(lang, "note_pay_to", name=member.display_name))
        self._credit(target, amount, "received", T(lang, "note_pay_from", name=ctx.author.display_name))
        await self.save_user_economy_data(ctx.author.id)
        await self.save_user_economy_data(member.id)
        await _reply(
            ctx,
            _info_view(
                T(lang, "transfer_title"),
                T(lang, "transfer_body",
                  amount=f"{amount:,}", target=member.mention,
                  balance=f"{data['balance']:,}"),
            ),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    # ── transactions ──────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="transactions", aliases=["tx", "history"],
        description=CMDS.text("transactions.description"),
        help=CMDS.help("transactions"),
    )
    async def transactions(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        txs = data.get("transactions", [])
        if not txs:
            return await _reply(ctx, _info_view(
                T(lang, "no_history_title"), T(lang, "no_history_body")))

        lines = []
        for t in txs[:25]:
            sign = "+" if t["amount"] >= 0 else "−"
            ts = datetime.datetime.utcfromtimestamp(int(t["ts"])).strftime("%m-%d %H:%M")
            lines.append(f"`{ts}` `{t['kind'][:10]:<10}` **{sign}{abs(int(t['amount'])):,}** 🪙  ·  {t.get('note','')}")
        await _reply(ctx, _info_view(
            T(lang, "activity_title", name=ctx.author.display_name),
            "\n".join(lines),
        ))

    # ── networth ──────────────────────────────────────────────────────────────
    @commands.hybrid_command(
        name="networth", aliases=["nw"],
        description=CMDS.text("networth.description"),
        help=CMDS.help("networth"),
    )
    async def networth(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        target = member or ctx.author
        data = await self.get_user_economy_data(target.id)
        nw = int(data["balance"]) + int(data["bank"])
        rank = await self._net_rank(str(target.id))
        body = T(
            lang, "networth_body",
            name=target.display_name,
            nw=f"{nw:,}",
            cash=f"{int(data['balance']):,}",
            bank=f"{int(data['bank']):,}",
            tier=bank_name(int(data.get("bank_tier", 0))),
            rank=f"#{rank}",
        )
        if not rank:
            body = T(lang, "networth_body_no_rank",
                     name=target.display_name, nw=f"{nw:,}",
                     cash=f"{int(data['balance']):,}",
                     bank=f"{int(data['bank']):,}",
                     tier=bank_name(int(data.get("bank_tier", 0))))
        await _reply(ctx, _info_view(T(lang, "networth_title"), body))
