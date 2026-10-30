"""
Economy — job commands (list, info, apply, quit).
"""
from discord.ext import commands
from ..data import (
    _info_view, _reply, _fmt_remaining, _check_achievements, _resolve_prefix, locale_t,
    JOBS, DEFAULT_JOB, get_job,
)
from utils.i18n import get_lang
from utils.locales import load_locales

from utils.command_locales import command_texts

CMDS = command_texts(__package__)

T = locale_t(load_locales("cogs.economy", "jobs"))


class JobsMixin:
    """job group commands."""

    @commands.hybrid_group(
        name="job",
        description=CMDS.text("job.description"),
        help=CMDS.help("job"), invoke_without_command=True
    )
    async def job(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._job_list(ctx)

    async def _job_list(self, ctx: commands.Context):
        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        cur = data.get("job")
        lines = []
        for jid, j in JOBS.items():
            current = T(lang, "current") if jid == cur else ""
            locked  = "" if data["level"] >= j["min_level"] else T(lang, "locked", level=j["min_level"])
            lines.append(T(
                lang, "line",
                emoji=j["emoji"], name=j["name"], id=jid,
                current=current, locked=locked,
                pay=j["min_pay"], pay_max=j["max_pay"], xp=j["xp_per_shift"],
                desc=j["description"],
            ))
        prefix = await _resolve_prefix(self.bot, ctx)
        await _reply(ctx, _info_view(
            T(lang, "board_title"),
            "\n\n".join(lines) + T(lang, "board_hint", prefix=prefix),
        ))

    @job.command(name="list", description=CMDS.text("job.list.description"))
    async def job_list(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()
        await self._job_list(ctx)

    @job.command(name="info", description=CMDS.text("job.info.description"))
    async def job_info(self, ctx: commands.Context, job_id: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        j = JOBS.get(job_id.lower())
        if not j:
            return await _reply(ctx, _info_view(
                T(lang, "unknown_title"), T(lang, "unknown_body", job=job_id)))
        body = T(
            lang, "info_body",
            emoji=j["emoji"], name=j["name"], desc=j["description"],
            level=j["min_level"], pay=f"{j['min_pay']:,}", pay_max=f"{j['max_pay']:,}",
            xp=j["xp_per_shift"], cooldown=_fmt_remaining(j.get("cooldown", 3600)),
        )
        await _reply(ctx, _info_view(T(lang, "info_title", name=j["name"]), body))

    @job.command(name="apply", description=CMDS.text("job.apply.description"))
    async def job_apply(self, ctx: commands.Context, job_id: str):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        jid = job_id.lower()
        j = JOBS.get(jid)
        if not j:
            return await _reply(ctx, _info_view(
                T(lang, "unknown_title"), T(lang, "unknown_body", job=job_id)))

        if data["level"] < j["min_level"]:
            return await _reply(ctx, _info_view(
                T(lang, "not_yet_title"),
                T(lang, "not_yet_body",
                  job=j["name"], level=j["min_level"], current=data["level"]),
            ))
        data["job"] = jid
        _check_achievements(data)
        await self.save_user_economy_data(ctx.author.id)
        await _reply(ctx, _info_view(
            T(lang, "hired_title"),
            T(lang, "hired_body", job=j["name"], emoji=j["emoji"]),
        ))

    @job.command(name="quit", description=CMDS.text("job.quit.description").format(job=get_job(DEFAULT_JOB)["name"]))
    async def job_quit(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.interaction.response.defer()

        lang = get_lang(ctx)
        data = await self.get_user_economy_data(ctx.author.id)
        if data.get("job") == DEFAULT_JOB:
            return await _reply(ctx, _info_view(
                T(lang, "nothing_quit_title"),
                T(lang, "nothing_quit_body", job=get_job(DEFAULT_JOB)["name"]),
            ))
        data["job"] = DEFAULT_JOB
        await self.save_user_economy_data(ctx.author.id)
        await _reply(ctx, _info_view(
            T(lang, "resigned_title"),
            T(lang, "resigned_body", job=get_job(DEFAULT_JOB)["name"]),
        ))
