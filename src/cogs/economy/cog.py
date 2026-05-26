from .data import *

class EconomyCog(commands.Cog):
    """Premium café economy with image cards, jobs, banking and a lottery."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        if not os.path.exists("data/economy_data"):
            log.info("Economy", "economy_data directory not found. Creating directory…")
            os.makedirs("data/economy_data")
            log.success("Economy", "economy_data directory created. Continuing…")

        self.economy_data: dict[str, dict] = self._load_all()
        self.lottery: dict = _load_lottery()

        # background task — bank interest (daily) + lottery draw check (hourly)
        self._tick_task.start()

    def cog_unload(self):
        try:
            self._tick_task.cancel()
        except Exception:
            pass

    # ── Persistence (legacy API kept for blackjack/slots/roulette/gambling) ──
    def _load_all(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        if not os.path.exists("data/economy_data"):
            return out
        for filename in os.listdir("data/economy_data"):
            if not filename.endswith(".json") or filename.startswith("_"):
                continue
            try:
                with open(os.path.join("data/economy_data", filename), "r") as f:
                    uid = filename[:-5]
                    raw = json.load(f)
                    out[uid] = _migrate_user(raw)
            except Exception as e:
                log.error("Economy", f"Error loading {filename}: {e}")
        return out

    # alias for backwards-compat with other cogs
    def load_economy_data(self) -> dict[str, dict]:
        return self._load_all()

    def save_economy_data(self) -> None:
        if not os.path.exists("data/economy_data"):
            os.makedirs("data/economy_data")
        for uid, data in self.economy_data.items():
            try:
                # always normalize before writing
                _migrate_user(data)
                with open(os.path.join("data/economy_data", f"{uid}.json"), "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as exc:
                log.error("Economy", f"Could not save {uid}: {exc}")

    def get_user_economy_data(self, user_id) -> dict:
        uid = str(user_id)
        if uid not in self.economy_data:
            self.economy_data[uid] = _default_user()
        return _migrate_user(self.economy_data[uid])

    # ── Internal helpers ────────────────────────────────────────────────────
    def _credit(self, data: dict, amount: int, kind: str, note: str = ""):
        amount = int(amount)
        data["balance"] = int(data.get("balance", 0)) + amount
        if amount > 0:
            data["total_earned"] = int(data.get("total_earned", 0)) + amount
        else:
            data["total_spent"] = int(data.get("total_spent", 0)) + abs(amount)
        _log_tx(data, kind, amount, note)

    def _net_rank(self, uid: str) -> int | None:
        sorted_users = sorted(
            ((u, d.get("balance", 0) + d.get("bank", 0)) for u, d in self.economy_data.items()),
            key=lambda x: x[1], reverse=True,
        )
        for i, (u, _) in enumerate(sorted_users, start=1):
            if u == uid:
                return i
        return None

    async def _send_balance_card(self, ctx, target: discord.Member, *, title: str = "Wallet"):
        data = self.get_user_economy_data(target.id)
        avatar_bytes = await fetch_avatar_bytes(str(target.display_avatar.replace(size=256, format="png")), size=256)

        lvl = int(data.get("level", 0))
        in_lvl = int(data.get("xp", 0)) - total_xp_for_level(lvl)
        nxt = xp_to_next(lvl)
        job = get_job(data.get("job"))
        cap = bank_cap(int(data.get("bank_tier", 0)))
        tier_name = bank_name(int(data.get("bank_tier", 0)))
        rank = self._net_rank(str(target.id))

        buf = await render_balance_card(
            avatar_bytes=avatar_bytes,
            name=target.display_name,
            cash=int(data.get("balance", 0)),
            bank=int(data.get("bank", 0)),
            bank_cap_v=cap,
            bank_tier_name=tier_name,
            net_worth=int(data.get("balance", 0)) + int(data.get("bank", 0)),
            level=lvl,
            xp_in_level=max(0, in_lvl),
            xp_for_next=nxt,
            job_name=job["name"],
            job_emoji="",  # PIL/DejaVu can't render color emoji — keep image text clean
            daily_streak=int(data.get("daily_streak", 0)),
            rank=rank,
            title=title,
        )
        prefix = await _resolve_prefix(self.bot, ctx)
        view = _card_view(
            title=f"{get_emoji('credit_card')} {title}",
            image_name="balance.png",
            footer_lines=[
                f"-# Use `{prefix}deposit` / `{prefix}withdraw` to manage your vault.",
                f"-# `{prefix}work` to earn, `{prefix}daily` for treats, `{prefix}shop` to spend.",
            ],
        )
        await ctx.send(view=view, file=discord.File(buf, "balance.png"))

    async def _send_reward_card(
        self,
        ctx,
        *,
        title: str,
        subtitle: str,
        amount: int,
        accent,
        footer: str = "",
        announce: str | None = None,
    ):
        data = self.get_user_economy_data(ctx.author.id)
        avatar_bytes = await fetch_avatar_bytes(
            str(ctx.author.display_avatar.replace(size=256, format="png")), size=256
        )
        new_balance = int(data.get("balance", 0))
        buf = await render_reward_card(
            avatar_bytes=avatar_bytes,
            name=ctx.author.display_name,
            title=title,
            subtitle=subtitle,
            amount=amount,
            new_balance=new_balance,
            accent=accent,
            footer=footer,
        )
        view = _card_view(
            title=f"### {title}".replace("###", "").strip() or title,
            image_name="reward.png",
            footer_lines=[announce] if announce else [],
        )
        await ctx.send(view=view, file=discord.File(buf, "reward.png"))

    # ── Background tick: bank interest + lottery draw ───────────────────────
    @tasks.loop(minutes=30)
    async def _tick_task(self):
        try:
            await self._apply_bank_interest()
            await self._maybe_draw_lottery()
        except Exception as exc:
            log.error("Economy", f"Tick task failed: {exc}")

    @_tick_task.before_loop
    async def _before_tick(self):
        await self.bot.wait_until_ready()
        # Stagger start so this never lines up with a heavy event burst
        await asyncio.sleep(20)

    async def _apply_bank_interest(self):
        """Daily compound interest based on bank tier."""
        now = int(time.time())
        today_utc = datetime.datetime.utcfromtimestamp(now).strftime("%Y-%m-%d")
        changed = 0
        for uid, data in self.economy_data.items():
            if data.get("last_interest_day") == today_utc:
                continue
            tier = int(data.get("bank_tier", 0))
            cap = bank_cap(tier)
            rate = bank_rate(tier)
            bank = int(data.get("bank", 0))
            if bank <= 0:
                data["last_interest_day"] = today_utc
                continue
            principal = min(bank, cap)
            interest = int(principal * rate)
            if interest <= 0:
                data["last_interest_day"] = today_utc
                continue
            data["bank"] = bank + interest
            data["total_earned"] = int(data.get("total_earned", 0)) + interest
            data["last_interest_day"] = today_utc
            _log_tx(data, "interest", interest, f"daily {bank_name(tier)} interest")
            changed += 1
        if changed:
            self.save_economy_data()
            log.info("Economy", f"Applied bank interest to {changed} accounts.")

    async def _maybe_draw_lottery(self):
        now = int(time.time())
        if now < int(self.lottery.get("next_draw", 0)):
            return
        # collect tickets
        entrants: list[tuple[str, int]] = []
        total_tickets = 0
        for uid, data in self.economy_data.items():
            tix = int(data.get("lottery_tickets", 0))
            if tix > 0:
                entrants.append((uid, tix))
                total_tickets += tix

        pot = int(self.lottery.get("pot", LOTTERY_BASE_POT))
        if not entrants or total_tickets <= 0 or pot <= 0:
            # roll over
            self.lottery["next_draw"] = now + LOTTERY_DRAW_INTERVAL
            _save_lottery(self.lottery)
            return

        # weighted pick
        roll = random.randint(1, total_tickets)
        cur = 0
        winner_id = entrants[-1][0]
        for uid, tix in entrants:
            cur += tix
            if roll <= cur:
                winner_id = uid
                break

        rake = int(pot * LOTTERY_HOUSE_RAKE)
        payout = pot - rake

        winner_data = self.get_user_economy_data(winner_id)
        self._credit(winner_data, payout, "lottery", f"weekly draw winner ({total_tickets} tickets)")

        # reset everyone's tickets
        for uid, _ in entrants:
            d = self.economy_data.get(uid)
            if d is not None:
                d["lottery_tickets"] = 0

        self.lottery = {
            "pot":         max(LOTTERY_BASE_POT, rake),
            "next_draw":   now + LOTTERY_DRAW_INTERVAL,
            "last_winner": winner_id,
            "last_pot":    payout,
        }
        _save_lottery(self.lottery)
        self.save_economy_data()
        log.info("Economy", f"Lottery: paid {payout:,} coins to {winner_id} (next pot starts at {self.lottery['pot']:,}).")

    # ─────────────────────────────────────────────────────────────────────
    # Commands
    # ─────────────────────────────────────────────────────────────────────

    # ── balance / profile ──
    @commands.hybrid_command(name="balance", aliases=["bal", "wallet"], description="Check your premium café wallet card",
                             help="{ 'en': 'check your pastry bag balance 🥐✨', 'de': 'sieh dein Wallet als Karte', 'es': 'consulta tu wallet 🥐✨' }")
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        await self._send_balance_card(ctx, target, title="Wallet")

    @commands.hybrid_command(name="profile", aliases=["prof", "stats"], description="Full café profile card",
                             help="{ 'en': 'view a full café profile card 📜✨', 'de': 'sieh dein volles Profil', 'es': 'mira tu perfil completo 📜✨' }")
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        # send the card
        await self._send_balance_card(ctx, target, title="Profile")
        # plus a small extras panel: badges + recent tx
        data = self.get_user_economy_data(target.id)
        ach = data.get("achievements", [])
        ach_line = ", ".join(f"{ACHIEVEMENTS[a]['emoji']} {ACHIEVEMENTS[a]['name']}" for a in ach if a in ACHIEVEMENTS) or "*no badges yet — go earn some!*"
        txs = data.get("transactions", [])[:5]
        if txs:
            lines = []
            for t in txs:
                sign = "+" if t["amount"] >= 0 else "−"
                lines.append(f"`{t['kind'][:10]:<10}` {sign}{abs(t['amount']):,}  ·  {t.get('note','')}")
            tx_block = "\n".join(lines)
        else:
            tx_block = "*no transactions yet*"
        view = _info_view(
            f"📜 {target.display_name}'s Extras",
            f"**Badges**\n{ach_line}\n\n**Recent activity**\n{tx_block}",
        )
        await ctx.send(view=view, allowed_mentions=discord.AllowedMentions.none())

    # ── daily ──
    @commands.hybrid_command(name="daily", description="Claim your daily treats with streak bonus",
                             help="{ 'en': 'claim your daily treats 🍬✨', 'de': 'hol dir deine täglichen Belohnungen', 'es': 'reclama tus golosinas diarias 🍬✨' }")
    async def daily(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        elapsed = now - int(data.get("last_daily", 0))

        if elapsed < COOLDOWN_DAILY:
            remain = COOLDOWN_DAILY - elapsed
            return await ctx.send(view=_info_view(
                "⏳ Daily on cooldown",
                f"Patience! Your treats are still baking.\nCome back in **{_fmt_remaining(remain)}**. ☕🍰",
            ))

        # streak: keep if claimed within 48h, else reset to 1
        streak = int(data.get("daily_streak", 0))
        if elapsed > 2 * COOLDOWN_DAILY:
            streak = 1
        else:
            streak += 1
        # multiplier caps at 7 days for a 2.4x bonus
        multiplier = 1 + min(streak, 7) * 0.2
        base = 1000
        reward = int(base * multiplier)

        self._credit(data, reward, "daily", f"day {streak} • x{multiplier:.1f}")
        data["daily_streak"] = streak
        data["last_daily"] = now
        _check_achievements(data)
        self.save_economy_data()

        await self._send_reward_card(
            ctx,
            title="🍬 Daily Treats",
            subtitle=f"Streak day {streak} 🔥  •  multiplier x{multiplier:.1f}",
            amount=reward,
            accent=ACCENT_GOLD,
            footer=msg(ctx, "daily_success", reward=reward),
        )

    # ── work ──
    @commands.hybrid_command(name="work", description="Work a shift at your current café job",
                             help="{ 'en': 'work a shift at your current café job ☕', 'de': 'arbeite eine Schicht', 'es': 'trabaja un turno en el café ☕' }")
    async def work(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        job = get_job(data.get("job"))
        cd = int(job.get("cooldown", COOLDOWN_WORK))

        # consumable: halve next work cooldown
        effects = data.setdefault("effects", {})
        if effects.get("work_cooldown_half"):
            cd = cd // 2

        elapsed = now - int(data.get("last_work", 0))
        if elapsed < cd:
            return await ctx.send(view=_info_view(
                "⏳ On a coffee break",
                f"You're resting after your last shift.\nBack to work in **{_fmt_remaining(cd - elapsed)}**. ☕💤",
            ))

        # one-shot: clear cooldown buff if it was used
        if effects.get("work_cooldown_half"):
            effects.pop("work_cooldown_half", None)

        reward = random.randint(int(job["min_pay"]), int(job["max_pay"]))
        self._credit(data, reward, "work", f"{job['name']} shift")
        data["last_work"] = now
        data["times_worked"] = int(data.get("times_worked", 0)) + 1

        # XP + level up
        new_lvl, gained_levels, leveled = add_xp(data, int(job.get("xp_per_shift", 10)))
        announce = msg(ctx, "level_up", level=new_lvl) if leveled else None

        newly = _check_achievements(data)
        self.save_economy_data()

        subtitle = f"{job['emoji']} {job['name']} shift  •  +{job.get('xp_per_shift', 10)} XP"
        footer = msg(ctx, "work_success", reward=reward)
        if newly:
            footer += "  •  unlocked: " + ", ".join(newly)
        await self._send_reward_card(
            ctx,
            title="🍯 Shift complete",
            subtitle=subtitle,
            amount=reward,
            accent=ACCENT_GREEN,
            footer=footer,
            announce=announce,
        )

    # ── jobs ──
    @commands.hybrid_group(name="job", description="Browse, apply for, and manage your café job",
                           help="{ 'en': 'manage your café career 💼', 'de': 'verwalte deinen Café-Job', 'es': 'gestiona tu carrera en el café 💼' }",
                           invoke_without_command=True)
    async def job(self, ctx: commands.Context):
        await self._job_list(ctx)

    async def _job_list(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        cur = data.get("job")
        lines = []
        for jid, j in JOBS.items():
            tag = "  ← **current**" if jid == cur else ""
            lock = "" if data["level"] >= j["min_level"] else f"  {get_emoji('vm_lock')} lvl {j['min_level']}"
            lines.append(f"{j['emoji']} **{j['name']}** `({jid})`{tag}{lock}\n-# {j['min_pay']}–{j['max_pay']} coins/shift • +{j['xp_per_shift']} XP\n-# *{j['description']}*")
        prefix = await _resolve_prefix(self.bot, ctx)
        await ctx.send(view=_info_view(
            "💼 Café Job Board",
            "\n\n".join(lines) + f"\n\n-# Apply with `{prefix}job apply <id>` once you meet the level requirement.",
        ))

    @job.command(name="list", description="See all available café jobs")
    async def job_list(self, ctx: commands.Context):
        await self._job_list(ctx)

    @job.command(name="info", description="Show details for a job")
    async def job_info(self, ctx: commands.Context, job_id: str):
        j = JOBS.get(job_id.lower())
        if not j:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))
        body = (f"{j['emoji']} **{j['name']}**\n*{j['description']}*\n\n"
                f"• Min level: **{j['min_level']}**\n"
                f"• Pay range: **{j['min_pay']:,} – {j['max_pay']:,}** coins/shift\n"
                f"• XP per shift: **+{j['xp_per_shift']}**\n"
                f"• Cooldown: **{_fmt_remaining(j.get('cooldown', 3600))}**")
        await ctx.send(view=_info_view(f"💼 {j['name']}", body))

    @job.command(name="apply", description="Apply for a job (must meet the level requirement)")
    async def job_apply(self, ctx: commands.Context, job_id: str):
        data = self.get_user_economy_data(ctx.author.id)
        jid = job_id.lower()
        j = JOBS.get(jid)
        if not j:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))
        if data["level"] < j["min_level"]:
            return await ctx.send(view=_info_view(
                f"{get_emoji('vm_lock')} Not yet",
                f"**{j['name']}** requires career level **{j['min_level']}**. You're level **{data['level']}**.",
            ))
        data["job"] = jid
        _check_achievements(data)
        self.save_economy_data()
        await ctx.send(view=_info_view(
            f"{get_emoji('icon_tick')} Hired!",
            f"You're now working as a **{j['name']}** {j['emoji']}\n-# Run `work` to clock in.",
        ))

    @job.command(name="quit", description="Quit your current job and go back to barista")
    async def job_quit(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        if data.get("job") == DEFAULT_JOB:
            return await ctx.send(view=_info_view("ℹ️ Nothing to quit", "You're already a barista."))
        data["job"] = DEFAULT_JOB
        self.save_economy_data()
        await ctx.send(view=_info_view("📤 Resigned", "You're back to **Barista** ☕."))

    # ── crime / rob ──
    @commands.hybrid_command(name="crime", description="Try to steal some extra treats",
                             help="{ 'en': 'try to steal some extra treats 😈', 'de': 'versuch, etwas zu stibitzen', 'es': 'intenta robar unas golosinas extra 😈' }")
    async def crime(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        if now - int(data.get("last_crime", 0)) < COOLDOWN_CRIME:
            remain = COOLDOWN_CRIME - (now - int(data["last_crime"]))
            return await ctx.send(view=_info_view(
                "👮 Lay low",
                f"The shopkeeper's watching. Try again in **{_fmt_remaining(remain)}**.",
            ))

        effects = data.setdefault("effects", {})
        boost = 0.25 if effects.pop("crime_boost", 0) else 0.0
        success = random.random() < (0.5 + boost)

        if success:
            reward = random.randint(200, 500)
            self._credit(data, reward, "crime", "successful heist")
            title, subtitle, amount, accent = ("😈 Got away!", "You swiped from the tip jar.", reward, ACCENT_GOLD)
        else:
            loss = random.randint(100, 300)
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "crime_fine", "caught and fined")
            title, subtitle, amount, accent = ("👮 Caught!", "You had to pay a fine.", -loss, ACCENT_RED)

        data["last_crime"] = now
        _check_achievements(data)
        self.save_economy_data()

        await self._send_reward_card(
            ctx, title=title, subtitle=subtitle, amount=amount, accent=accent,
            footer="Tip: use a lockpick before your next attempt for +25% success.",
        )

    @commands.hybrid_command(name="rob", description="Try to rob another user",
                             help="{ 'en': 'try to rob another user 🔫', 'de': 'rauber jemanden aus', 'es': 'intenta robar a otro 🔫' }")
    async def rob(self, ctx: commands.Context, member: discord.Member):
        if member.id == ctx.author.id:
            return await ctx.send(view=_info_view("☕ Really?", "You can't rob yourself, silly!"))
        if member.bot:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_bot')} No can do", "Bots have nothing in their pockets."))

        data   = self.get_user_economy_data(ctx.author.id)
        target = self.get_user_economy_data(member.id)
        now = int(time.time())

        if data["balance"] < 100:
            return await ctx.send(view=_info_view("💸 Broke", "You need at least **100** coins to plan a robbery."))
        if target["balance"] < 100:
            return await ctx.send(view=_info_view("🥺 Mercy", "They don't have enough to rob — leave them alone!"))
        if now - int(data.get("last_rob", 0)) < COOLDOWN_ROB:
            remain = COOLDOWN_ROB - (now - int(data["last_rob"]))
            return await ctx.send(view=_info_view("🕵️ Lay low", f"Try again in **{_fmt_remaining(remain)}**."))

        # target's rob_shield burns first
        target_effects = target.setdefault("effects", {})
        if target_effects.pop("rob_shield", 0):
            data["last_rob"] = now
            self.save_economy_data()
            return await ctx.send(view=_info_view(
                "🛡️ Blocked!",
                f"{member.display_name} had a **Tip Jar Lock** active. The robbery failed and they kept everything.",
            ))

        success = random.random() < 0.4
        if success:
            amount = random.randint(10, min(target["balance"], 500))
            self._credit(data, amount, "rob", f"from {member.display_name}")
            self._credit(target, -amount, "robbed", f"by {ctx.author.display_name}")
            title, subtitle, accent = ("💰 Score!", f"You robbed {member.display_name}.", ACCENT_GOLD)
            shown_amount = amount
        else:
            loss = 150
            loss = min(loss, int(data.get("balance", 0)))
            self._credit(data, -loss, "rob_fail", f"caught by {member.display_name}")
            self._credit(target, loss, "rob_apology", f"from {ctx.author.display_name}")
            title, subtitle, accent = ("👮 Caught!", f"You had to pay {member.display_name} as apology.", ACCENT_RED)
            shown_amount = -loss

        data["last_rob"] = now
        _check_achievements(data)
        self.save_economy_data()
        await self._send_reward_card(ctx, title=title, subtitle=subtitle, amount=shown_amount, accent=accent)

    # ── pay ──
    @commands.hybrid_command(name="pay", aliases=["give"], description="Send coins to another user",
                             help="{ 'en': 'send coins to another user 💸🥐', 'de': 'sende Münzen an jemanden', 'es': 'envía monedas a alguien 💸🥐' }")
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        if not member or member.bot or member.id == ctx.author.id:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad target", "Pick a real person other than yourself."))
        if amount <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Amount must be positive."))

        data   = self.get_user_economy_data(ctx.author.id)
        target = self.get_user_economy_data(member.id)
        if data["balance"] < amount:
            return await ctx.send(view=_info_view("💸 Not enough cash", "Your pastry bag is too light for that."))

        self._credit(data, -amount, "pay", f"to {member.display_name}")
        self._credit(target, amount, "received", f"from {ctx.author.display_name}")
        self.save_economy_data()

        await ctx.send(view=_info_view(
            "💸 Transfer complete",
            f"You sent **{amount:,}** 🥐 to {member.mention}.\n-# New balance: **{data['balance']:,}** 🥐",
        ), allowed_mentions=discord.AllowedMentions.none())

    # ── leaderboard (image card, paginated) ──
    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"], description="See the café rich list as image cards",
                             help="{ 'en': 'see who has the most treats 🏆🥐', 'de': 'sieh die reichsten Gäste', 'es': 'mira quién tiene más 🏆🥐' }")
    async def leaderboard(self, ctx: commands.Context):
        sorted_users = sorted(
            self.economy_data.items(),
            key=lambda x: x[1].get("balance", 0) + x[1].get("bank", 0),
            reverse=True,
        )
        if not sorted_users:
            return await ctx.send(view=_info_view("☕ Quiet café", "No one has any coins yet — the café is just opening!"))

        # take top 10 only for the visual card
        top = sorted_users[:10]
        # fetch avatars in parallel
        async def _entry(idx_uid):
            i, (uid, d) = idx_uid
            user = self.bot.get_user(int(uid)) or await self.bot.fetch_user(int(uid)) if uid.isdigit() else None
            if user is None:
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

        entries = await asyncio.gather(*(_entry(item) for item in enumerate(top)))
        buf = await render_leaderboard_card(title="🏆 Café Rich List", entries=entries, page=1, pages=1)

        view = _card_view(
            title="🏆 Leaderboard",
            image_name="leaderboard.png",
            footer_lines=[f"-# Showing top **{len(entries)}** of **{len(sorted_users)}** café-goers."],
        )
        await ctx.send(view=view, file=discord.File(buf, "leaderboard.png"), allowed_mentions=discord.AllowedMentions.none())

    # ── shop / buy / sell / use / inventory ──
    @commands.hybrid_command(name="shop", description="Browse the café boutique",
                             help="{ 'en': 'browse the café boutique 🛍️✨', 'de': 'stöbere in der Boutique', 'es': 'explora la boutique 🛍️✨' }")
    async def shop(self, ctx: commands.Context, category: str = None):
        prefix = await _resolve_prefix(self.bot, ctx)
        cats = ("consumable", "upgrade", "collectible")
        if category and category.lower() not in cats:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown category", f"Try one of: {', '.join('`' + c + '`' for c in cats)}"))
        cat_filter = category.lower() if category else None

        sections: dict[str, list[str]] = {c: [] for c in cats}
        data = self.get_user_economy_data(ctx.author.id)
        lvl = int(data.get("level", 0))
        for iid, item in SHOP_ITEMS.items():
            if cat_filter and item["category"] != cat_filter:
                continue
            lock = "" if lvl >= item.get("min_level", 0) else f"  {get_emoji('icon_lock')} lvl {item['min_level']}"
            sections[item["category"]].append(
                f"{item['emoji']} **{item['name']}** `({iid})` — **{item['price']:,}** 🥐{lock}\n-# *{item['description']}*"
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

    @commands.hybrid_command(name="buy", description="Buy an item from the shop",
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
            f"You bought **{count}x {item['emoji']} {item['name']}** for **{total:,}** 🥐.\n-# New balance: **{data['balance']:,}** 🥐",
        ))

    @commands.hybrid_command(name="sell", description="Sell an item back from your inventory",
                             help="{ 'en': 'sell a treat back for some coins 💰', 'de': 'verkauf etwas aus deinem Bag', 'es': 'vende algo de tu inventario 💰' }")
    async def sell(self, ctx: commands.Context, item_id: str, count: int = 1):
        if count <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
        iid = item_id.lower()
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
            f"You sold **{count}x {item['emoji']} {item['name']}** for **{gain:,}** 🥐.\n-# New balance: **{data['balance']:,}** 🥐",
        ))

    @commands.hybrid_command(name="use", description="Use a consumable or upgrade item",
                             help="{ 'en': 'use a consumable from your bag 🧪', 'de': 'benutze ein Item aus deinem Bag', 'es': 'usa un objeto de tu inventario 🧪' }")
    async def use(self, ctx: commands.Context, item_id: str):
        iid = item_id.lower()
        item = get_item(iid)
        if not item:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown item", f"No item called `{item_id}`."))
        data = self.get_user_economy_data(ctx.author.id)
        if int(data["inventory"].get(iid, 0)) < 1:
            return await ctx.send(view=_info_view("📦 None in bag", f"You don't have any **{item['name']}**."))
        if item["category"] == "collectible":
            return await ctx.send(view=_info_view("🎖️ Collectible", "Collectibles can't be used — they're for showing off on your profile."))

        effect = item.get("effect")
        msg_text = ""
        effects = data.setdefault("effects", {})

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
            msg_text = f"Your vault is now a **{bank_name(data['bank_tier'])}** with cap **{bank_cap(data['bank_tier']):,}** and **{int(bank_rate(data['bank_tier'])*100*10)/10}%** daily interest. 🏦✨"
        else:
            return await ctx.send(view=_info_view("🤔 No effect", "This item doesn't seem to do anything right now."))

        # consume one
        data["inventory"][iid] = int(data["inventory"][iid]) - 1
        if data["inventory"][iid] <= 0:
            del data["inventory"][iid]
        self.save_economy_data()
        await ctx.send(view=_info_view(f"{item['emoji']} {item['name']} used", msg_text))

    @commands.hybrid_command(name="inventory", aliases=["inv", "bag"], description="View your inventory grouped by category",
                             help="{ 'en': 'check your collection of treats 🎒✨', 'de': 'sieh dir deinen Bag an', 'es': 'revisa tu inventario 🎒✨' }")
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        data = self.get_user_economy_data(target.id)
        inv = data.get("inventory", {})
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

    # ── bank: deposit / withdraw / upgrade ──
    @commands.hybrid_group(name="bank", description="Manage your café vault: deposit, withdraw, upgrade",
                           help="{ 'en': 'manage your café vault 🏦', 'de': 'verwalte deinen Tresor', 'es': 'gestiona tu bóveda 🏦' }",
                           invoke_without_command=True)
    async def bank(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        tier = int(data.get("bank_tier", 0))
        cap = bank_cap(tier)
        rate = bank_rate(tier)
        body = (f"**{bank_name(tier)}** — tier **{tier+1}/{len(BANK_TIERS)}**\n"
                f"• Stored: **{int(data['bank']):,}** / **{cap:,}** 🏦\n"
                f"• Daily interest: **{rate*100:.2f}%** (auto-credited every 24h)\n\n"
                f"-# Use `bank deposit`, `bank withdraw` or `bank upgrade` to manage.")
        await ctx.send(view=_info_view("🏦 Your Vault", body))

    @bank.command(name="deposit", description="Move cash from wallet into the vault")
    async def bank_deposit(self, ctx: commands.Context, amount: str):
        data = self.get_user_economy_data(ctx.author.id)
        cap = bank_cap(int(data.get("bank_tier", 0)))
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
        cur = int(data.get("bank_tier", 0))
        if cur >= max_bank_tier():
            return await ctx.send(view=_info_view("🏆 Maxed out", "Your vault is already a **Diamond Vault** — the highest tier."))
        next_tier = cur + 1
        # cost = 50% of next-tier cap
        cost = bank_cap(next_tier) // 2
        if data["balance"] + data["bank"] < cost:
            return await ctx.send(view=_info_view(
                "💸 Not enough net worth",
                f"Upgrading to **{bank_name(next_tier)}** costs **{cost:,}** 🥐 (paid from wallet first, then vault).",
            ))

        # pay from wallet first
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

    # ── lottery ──
    @commands.hybrid_group(name="lottery", aliases=["lotto"], description="Play the weekly café lottery",
                           help="{ 'en': 'play the weekly café lottery 🎰', 'de': 'spiele die wöchentliche Lotterie', 'es': 'juega la lotería semanal 🎰' }",
                           invoke_without_command=True)
    async def lottery(self, ctx: commands.Context):
        await self._lottery_info(ctx)

    async def _lottery_info(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        now = int(time.time())
        remain = max(0, int(self.lottery.get("next_draw", now)) - now)
        last = self.lottery.get("last_winner")
        last_block = ""
        if last:
            user = self.bot.get_user(int(last)) if last.isdigit() else None
            who = user.display_name if user else last
            last_block = f"\n-# Last winner: **{who}** scooped **{int(self.lottery.get('last_pot', 0)):,}** 🥐"
        body = (f"💸 **Pot**: **{int(self.lottery['pot']):,}** 🥐\n"
                f"🕒 **Next draw**: in **{_fmt_remaining(remain)}**\n"
                f"🎟️ **Your tickets**: **{int(data.get('lottery_tickets', 0))}**\n\n"
                f"Tickets cost **{LOTTERY_TICKET_PRICE:,}** 🥐 each. Buy with `lottery buy <count>`.{last_block}")
        await ctx.send(view=_info_view("🎰 Café Lottery", body))

    @lottery.command(name="info", description="Show the current lottery pot, draw time and your tickets")
    async def lottery_info(self, ctx: commands.Context):
        await self._lottery_info(ctx)

    @lottery.command(name="buy", description="Buy lottery tickets")
    async def lottery_buy(self, ctx: commands.Context, count: int = 1):
        if count <= 0:
            return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Bad amount", "Count must be at least 1."))
        cost = LOTTERY_TICKET_PRICE * count
        data = self.get_user_economy_data(ctx.author.id)
        if data["balance"] < cost:
            return await ctx.send(view=_info_view("💸 Not enough cash", f"That costs **{cost:,}** 🥐."))
        # lucky charm: doubles ticket count
        effects = data.setdefault("effects", {})
        bonus_mult = 2 if effects.pop("lottery_boost", 0) else 1
        added = count * bonus_mult

        self._credit(data, -cost, "lottery_buy", f"{count} tickets" + (" (lucky x2)" if bonus_mult > 1 else ""))
        data["lottery_tickets"] = int(data.get("lottery_tickets", 0)) + added
        # add to pot (full price goes in, no cut)
        self.lottery["pot"] = int(self.lottery.get("pot", 0)) + cost
        _save_lottery(self.lottery)
        self.save_economy_data()

        await ctx.send(view=_info_view(
            "🎟️ Tickets bought",
            f"You now hold **{int(data['lottery_tickets'])}** tickets.\n"
            f"• Spent **{cost:,}** 🥐\n"
            f"• Pot is now **{int(self.lottery['pot']):,}** 🥐"
            + (f"\n-# Lucky charm doubled your tickets! 🍀" if bonus_mult > 1 else ""),
        ))

    # ── transactions ──
    @commands.hybrid_command(name="transactions", aliases=["tx", "history"], description="See your recent transactions",
                             help="{ 'en': 'see your last transactions 📜', 'de': 'sieh deine letzten Transaktionen', 'es': 'mira tus últimas transacciones 📜' }")
    async def transactions(self, ctx: commands.Context):
        data = self.get_user_economy_data(ctx.author.id)
        txs = data.get("transactions", [])
        if not txs:
            return await ctx.send(view=_info_view("📜 No history", "No transactions yet."))
        lines = []
        for t in txs[:25]:
            sign = "+" if t["amount"] >= 0 else "−"
            ts = datetime.datetime.utcfromtimestamp(int(t["ts"])).strftime("%m-%d %H:%M")
            lines.append(f"`{ts}` `{t['kind'][:10]:<10}` **{sign}{abs(int(t['amount'])):,}** 🥐  ·  {t.get('note','')}")
        await ctx.send(view=_info_view(f"📜 {ctx.author.display_name}'s Recent Activity", "\n".join(lines)))

    # ── networth ──
    @commands.hybrid_command(name="networth", aliases=["nw"], description="Quick net worth summary",
                             help="{ 'en': 'calculate your total café fortune 📊🥐', 'de': 'berechne dein gesamtes Vermögen', 'es': 'calcula tu fortuna 📊🥐' }")
    async def networth(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        data = self.get_user_economy_data(target.id)
        nw = int(data["balance"]) + int(data["bank"])
        rank = self._net_rank(str(target.id))
        body = (f"💼 **{target.display_name}** is worth **{nw:,}** 🥐\n"
                f"• Cash: **{int(data['balance']):,}**\n"
                f"• Bank: **{int(data['bank']):,}** ({bank_name(int(data.get('bank_tier', 0)))})\n"
                f"• Rank: **#{rank}**" if rank else "")
        await ctx.send(view=_info_view("📊 Net Worth", body))


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
