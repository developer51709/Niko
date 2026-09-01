"""
Economy — job commands (list, info, apply, quit).
"""
from discord.ext import commands
from ..data import (
    _info_view, _fmt_remaining, _check_achievements, _resolve_prefix,
    JOBS, DEFAULT_JOB, get_job, get_emoji,
)


class JobsMixin:
    """job group commands."""

    @commands.hybrid_group(
        name="job",
        description="Browse, apply for, and manage your café job",
        help="{ 'en': 'manage your café career 💼', 'de': 'verwalte deinen Café-Job', 'es': 'gestiona tu carrera en el café 💼' }",
        invoke_without_command=True
    )
    async def job(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._job_list(ctx)

    async def _job_list(self, ctx: commands.Context):
        data = await self.get_user_economy_data(ctx.author.id)
        cur = data.get("job")
        lines = []
        for jid, j in JOBS.items():
            tag  = "  ← **current**" if jid == cur else ""
            lock = "" if data["level"] >= j["min_level"] else f"  {get_emoji('vm_lock')} lvl {j['min_level']}"
            lines.append(
                f"{j['emoji']} **{j['name']}** `({jid})`{tag}{lock}\n"
                f"-# {j['min_pay']}–{j['max_pay']} coins/shift • +{j['xp_per_shift']} XP\n"
                f"-# *{j['description']}*"
            )
        prefix = await _resolve_prefix(self.bot, ctx)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(
                "💼 Café Job Board",
                "\n\n".join(lines) + f"\n\n-# Apply with `{prefix}job apply <id>` once you meet the level requirement.",
            ))
        else:
            await ctx.send(view=_info_view(
                "💼 Café Job Board",
                "\n\n".join(lines) + f"\n\n-# Apply with `{prefix}job apply <id>` once you meet the level requirement.",
            ))

    @job.command(name="list", description="See all available café jobs")
    async def job_list(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._job_list(ctx)

    @job.command(name="info", description="Show details for a job")
    async def job_info(self, ctx: commands.Context, job_id: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        j = JOBS.get(job_id.lower())
        if not j:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))
        body = (
            f"{j['emoji']} **{j['name']}**\n*{j['description']}*\n\n"
            f"• Min level: **{j['min_level']}**\n"
            f"• Pay range: **{j['min_pay']:,} – {j['max_pay']:,}** coins/shift\n"
            f"• XP per shift: **+{j['xp_per_shift']}**\n"
            f"• Cooldown: **{_fmt_remaining(j.get('cooldown', 3600))}**"
        )
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(f"💼 {j['name']}", body))
        else:
            await ctx.send(view=_info_view(f"💼 {j['name']}", body))

    @job.command(name="apply", description="Apply for a job (must meet the level requirement)")
    async def job_apply(self, ctx: commands.Context, job_id: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        data = await self.get_user_economy_data(ctx.author.id)
        jid = job_id.lower()
        j = JOBS.get(jid)
        if not j:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Unknown job", f"No job called `{job_id}`. Try `job list`."))

        if data["level"] < j["min_level"]:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(
                    f"{get_emoji('vm_lock')} Not yet",
                    f"**{j['name']}** requires career level **{j['min_level']}**. You're level **{data['level']}**.",
                ))
            else:
                return await ctx.send(view=_info_view(
                    f"{get_emoji('vm_lock')} Not yet",
                    f"**{j['name']}** requires career level **{j['min_level']}**. You're level **{data['level']}**.",
                ))
        data["job"] = jid
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view(
                f"{get_emoji('icon_tick')} Hired!",
                f"You're now working as a **{j['name']}** {j['emoji']}\n-# Run `work` to clock in.",
            ))
        else:
            await ctx.send(view=_info_view(
                f"{get_emoji('icon_tick')} Hired!",
                f"You're now working as a **{j['name']}** {j['emoji']}\n-# Run `work` to clock in.",
            ))

    @job.command(name="quit", description="Quit your current job and go back to barista")
    async def job_quit(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        data = await self.get_user_economy_data(ctx.author.id)
        if data.get("job") == DEFAULT_JOB:
            if ctx.interaction:
                return await ctx.interaction.followup.send(view=_info_view(f"{get_emoji('icon_cross')} Nothing to quit", "You're already a barista."))
            else:
                return await ctx.send(view=_info_view(f"{get_emoji('icon_cross')} Nothing to quit", "You're already a barista."))
        data["job"] = DEFAULT_JOB
        await self.save_user_economy_data(ctx.author.id)
        if ctx.interaction:
            await ctx.interaction.followup.send(view=_info_view("📤 Resigned", "You're back to **Barista** ☕."))
        else:
            await ctx.send(view=_info_view("📤 Resigned", "You're back to **Barista** ☕."))
