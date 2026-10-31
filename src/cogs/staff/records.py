"""The staff roster: roles, states, and the database calls behind them.

A staff record has three states. ``suspended`` keeps the assigned role for when
the investigation ends, but withdraws both Discord and website access.
``former`` is a normal demotion: it also keeps the public profile so a future
rehire does not lose it, while both states stay hidden from the public roster.
"""

import time

import discord
from discord.ext import commands

from config.ids import OWNER_IDS, SUPPORT_GUILD
from cogs.staff.support_server import get_support_ids

STAFF_ROLES = {
    "head_admin": "Head Admin",
    "moderator": "Moderator",
    "head_support": "Head of Support",
    "graphic_designer": "Graphic Designer",
    "support": "Support Team",
    "event_coordinator": "Event Coordinator",
    "partnerships_promotions_lead": "Partnerships & Promotions Lead",
    "partnership_manager": "Partnership Manager",
}
ROLE_ORDER = ("head_admin", "moderator", "graphic_designer", "head_support", "support", "event_coordinator", "partnerships_promotions_lead", "partnership_manager")

STAFF_STATUS_ACTIVE = "active"
STAFF_STATUS_SUSPENDED = "suspended"
STAFF_STATUS_FORMER = "former"
STAFF_STATUSES = {STAFF_STATUS_ACTIVE, STAFF_STATUS_SUSPENDED, STAFF_STATUS_FORMER}


def is_owner_user(user, bot) -> bool:
    return user.id in OWNER_IDS


def staff_status(row) -> str:
    """Return a known staff-record state, defaulting legacy rows to active."""
    value = str(row.get("staff_status") or STAFF_STATUS_ACTIVE).strip().lower() if row else STAFF_STATUS_ACTIVE
    return value if value in STAFF_STATUSES else STAFF_STATUS_ACTIVE


async def get_staff_role(bot, user_id: int) -> str | None:
    """Resolve an active staff role, or ``None`` for everyone else.

    Suspended and former records keep their role for restoration, but must not
    pass any staff gate, so this function is the single access check used by
    both the Discord commands and the web application.
    """
    pool = getattr(bot, "cxn", None)
    if pool is None:
        return None
    try:
        row = await pool.fetchrow(
            "SELECT role, staff_status FROM staff_members WHERE user_id = $1", int(user_id)
        )
    except Exception as exc:
        # Only the pre-migration schema may fall back to a role-only lookup.
        # Swallowing every database error here could let a suspended member
        # through during a transient outage, so re-raise anything else.
        if "staff_status" not in str(exc).lower():
            raise
        row = await pool.fetchrow(
            "SELECT role FROM staff_members WHERE user_id = $1", int(user_id)
        )
    if not row or staff_status(row) != STAFF_STATUS_ACTIVE:
        return None
    return str(row["role"]) if row.get("role") in STAFF_ROLES else None


async def get_staff_record(bot, user_id: int) -> dict | None:
    """Return the stored role and state for an existing staff record."""
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The staff database is not ready yet.")
    row = await pool.fetchrow(
        "SELECT role, staff_status FROM staff_members WHERE user_id = $1", int(user_id)
    )
    if not row or row.get("role") not in STAFF_ROLES:
        return None
    return {"role": str(row["role"]), "staff_status": staff_status(row)}


async def persist_staff_role(pool, user_id: int, role: str, assigned_by: int) -> str:
    """Save a staff role without replacing the member's public profile.

    An existing suspension is deliberately preserved: changing or reappointing
    a role is not the same decision as ending an investigation, so only the
    explicit lift action restores access.
    """
    if role not in STAFF_ROLES:
        raise ValueError(f"Unknown Niko staff role: {role}")
    if int(user_id) in OWNER_IDS:
        raise ValueError("Owner accounts cannot be assigned through the staff roster.")
    existing = await pool.fetchrow(
        "SELECT staff_status FROM staff_members WHERE user_id = $1", int(user_id)
    )
    status = STAFF_STATUS_SUSPENDED if existing and staff_status(existing) == STAFF_STATUS_SUSPENDED else STAFF_STATUS_ACTIVE
    now = int(time.time())
    # Two statements keep the public profile intact: INSERT OR REPLACE would
    # replace the whole row, which is how a role change used to erase a bio,
    # banner, links, and the member's own visibility preference.
    await pool.execute(
        "UPDATE staff_members SET role = $1, assigned_by = $2, assigned_at = $3, "
        "staff_status = $4, status_reason = NULL, status_changed_by = $5, "
        "status_changed_at = $6 WHERE user_id = $7",
        role, int(assigned_by), now, status, int(assigned_by), now, int(user_id),
    )
    await pool.execute(
        "INSERT OR IGNORE INTO staff_members "
        "(user_id, role, assigned_by, assigned_at, staff_status, status_changed_by, status_changed_at) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7)",
        int(user_id), role, int(assigned_by), now, status, int(assigned_by), now,
    )
    return status


async def _support_member(bot, user_id: int):
    """Resolve a support-guild member, including when the local cache is cold."""
    support_guild = bot.get_guild(SUPPORT_GUILD)
    if support_guild is None:
        return None
    member = support_guild.get_member(int(user_id))
    if member is not None:
        return member
    try:
        return await support_guild.fetch_member(int(user_id))
    except Exception:
        return None


async def set_staff_role(bot, user_id: int, role: str | None, assigned_by: int, reason: str = "") -> str:
    """Assign, change, or demote a staff member while retaining their profile."""
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The staff database is not ready yet.")
    if int(user_id) in OWNER_IDS:
        raise ValueError("Owner accounts cannot be changed through the staff roster.")
    if role is not None and role not in STAFF_ROLES:
        raise ValueError(f"Unknown Niko staff role: {role}")

    member = await _support_member(bot, user_id)
    if role is None:
        existing = await pool.fetchrow(
            "SELECT role, staff_status FROM staff_members WHERE user_id = $1", int(user_id)
        )
        if existing:
            await pool.execute(
                "UPDATE staff_members SET staff_status = $1, status_reason = $2, "
                "status_changed_by = $3, status_changed_at = $4 WHERE user_id = $5",
                STAFF_STATUS_FORMER, reason.strip()[:1000] or None,
                int(assigned_by), int(time.time()), int(user_id),
            )
        if member:
            await sync_member_staff_roles(bot, member, None)
        return STAFF_STATUS_FORMER

    status = await persist_staff_role(pool, user_id, role, assigned_by)
    if member:
        await sync_member_staff_roles(bot, member, role if status == STAFF_STATUS_ACTIVE else None)
    return status


async def set_staff_suspension(
    bot, user_id: int, suspended: bool, actor_id: int, reason: str = "",
) -> str:
    """Suspend or lift a staff member without changing their assigned role."""
    pool = getattr(bot, "cxn", None)
    if pool is None:
        raise RuntimeError("The staff database is not ready yet.")
    if int(user_id) in OWNER_IDS:
        raise ValueError("Owner accounts cannot be suspended.")
    record = await get_staff_record(bot, user_id)
    if record is None:
        raise ValueError("That member does not have a staff role to suspend.")
    if suspended and record["staff_status"] != STAFF_STATUS_ACTIVE:
        raise ValueError("Only active staff members can be suspended.")
    if not suspended and record["staff_status"] != STAFF_STATUS_SUSPENDED:
        raise ValueError("That staff member is not currently suspended.")
    now = int(time.time())
    if suspended:
        await pool.execute(
            "UPDATE staff_members SET staff_status = $1, status_reason = $2, "
            "status_changed_by = $3, status_changed_at = $4 WHERE user_id = $5",
            STAFF_STATUS_SUSPENDED, reason.strip()[:1000] or None,
            int(actor_id), now, int(user_id),
        )
    else:
        await pool.execute(
            "UPDATE staff_members SET staff_status = $1, status_reason = NULL, "
            "status_changed_by = $2, status_changed_at = $3 WHERE user_id = $4",
            STAFF_STATUS_ACTIVE, int(actor_id), now, int(user_id),
        )
    member = await _support_member(bot, user_id)
    if member:
        await sync_member_staff_roles(
            bot, member, None if suspended else record["role"],
        )
    return STAFF_STATUS_SUSPENDED if suspended else STAFF_STATUS_ACTIVE


async def is_staff_member(ctx: commands.Context) -> bool:
    if is_owner_user(ctx.author, ctx.bot):
        return True
    return await get_staff_role(ctx.bot, ctx.author.id) is not None


async def role_for(ctx: commands.Context) -> str | None:
    """The staff role key of the caller, or ``"owner"`` for the bot owner."""
    if is_owner_user(ctx.author, ctx.bot):
        return "owner"
    return await get_staff_role(ctx.bot, ctx.author.id)


async def sync_member_staff_roles(bot, member: discord.Member, staff_key: str | None) -> None:
    """Give the member exactly the support-guild roles their roster role means."""
    if member.guild.id != SUPPORT_GUILD:
        return
    roles = (await get_support_ids(bot))["roles"]

    to_add, to_remove = [], []
    shared_id = roles.get("staff")
    shared = member.guild.get_role(int(shared_id)) if shared_id else None
    valid_staff_key = staff_key if staff_key in ROLE_ORDER else None
    if shared and valid_staff_key and shared not in member.roles:
        to_add.append(shared)
    elif shared and not valid_staff_key and shared in member.roles:
        to_remove.append(shared)
    for key in ROLE_ORDER:
        role_id = roles.get(key)
        role = member.guild.get_role(int(role_id)) if role_id else None
        if role and key == valid_staff_key and role not in member.roles:
            to_add.append(role)
        elif role and key != valid_staff_key and role in member.roles:
            to_remove.append(role)
    if to_remove:
        await member.remove_roles(*to_remove, reason="Niko staff assignment changed")
    if to_add:
        await member.add_roles(*to_add, reason="Niko staff assignment changed")
