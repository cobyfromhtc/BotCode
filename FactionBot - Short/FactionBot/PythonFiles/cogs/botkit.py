# -*- coding: utf-8 -*-
"""botkit — shared helpers for FactionBot cogs.

Every cog uses this module for:
  * DB access (same SQLite file as the legacy DataManager: data/bot_data.db,
    WAL journal, busy_timeout — safe alongside the main bot's connection)
  * consistent embed styling
  * small utilities (time formatting, JSON list columns, hierarchy checks)

Cogs must NEVER import from Bot.py (circular import) — anything they need
from the core is either in here or stashed on the bot instance
(bot.embed_builder, bot.ticket_tool, ...).
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import discord

# ---------------------------------------------------------------------------
# Paths & DB
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # cogs/ -> PythonFiles/ -> FactionBot/
DB_PATH = PROJECT_ROOT / "data" / "bot_data.db"

_brand_footer: Optional[str] = None  # cached footer text (set by core at load)


def get_conn() -> sqlite3.Connection:
    """Open a NEW short-lived SQLite connection with the standard pragmas.

    Pattern: open → use → close (see run() / fetch helpers). Short-lived
    connections + WAL + busy_timeout avoid cross-connection lock contention
    with the bot's long-lived DataManager connection.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def run(sql: str, args: Sequence[Any] = ()) -> None:
    conn = get_conn()
    try:
        conn.execute(sql, tuple(args))
        conn.commit()
    finally:
        conn.close()


def fetchall(sql: str, args: Sequence[Any] = ()) -> List[sqlite3.Row]:
    conn = get_conn()
    try:
        return conn.execute(sql, tuple(args)).fetchall()
    finally:
        conn.close()


def fetchone(sql: str, args: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
    conn = get_conn()
    try:
        return conn.execute(sql, tuple(args)).fetchone()
    finally:
        conn.close()


def create_tables(statements: Sequence[str]) -> None:
    """Idempotently create tables (each statement must be IF NOT EXISTS)."""
    conn = get_conn()
    try:
        for s in statements:
            conn.execute(s)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# JSON column helpers (the DB stores lists/dicts as JSON text)
# ---------------------------------------------------------------------------
def jdump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def jload(value: Optional[str], default: Any = None) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def fmt_duration(seconds: float) -> str:
    seconds = int(max(0, seconds))
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    if seconds < 86400:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    days = seconds // 86400
    return f"{days}d {(seconds % 86400) // 3600}h"


def fmt_dt(value: Optional[datetime]) -> str:
    if value is None:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return f"<t:{int(value.timestamp())}:R>"


# ---------------------------------------------------------------------------
# Embeds (consistent FactionBot styling)
# ---------------------------------------------------------------------------
COLOR_SUCCESS = discord.Color.from_str("#2ECC71")
COLOR_ERROR = discord.Color.from_str("#E74C3C")
COLOR_INFO = discord.Color.from_str("#3498DB")
COLOR_WARNING = discord.Color.from_str("#F39C12")
COLOR_NEUTRAL = discord.Color.from_str("#95A5A6")
COLOR_BRAND = discord.Color.from_str("#9B59B6")


def set_footer(text: Optional[str]) -> None:
    global _brand_footer
    _brand_footer = text


def _base(title: str, description: str, color: discord.Color) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color,
                          timestamp=datetime.now(timezone.utc))
    if _brand_footer:
        embed.set_footer(text=_brand_footer)
    return embed


def success(title: str, description: str = "") -> discord.Embed:
    return _base(f"✅ {title}" if title else title, description, COLOR_SUCCESS)


def error(title: str, description: str = "") -> discord.Embed:
    return _base(f"❌ {title}" if title else title, description, COLOR_ERROR)


def info(title: str, description: str = "") -> discord.Embed:
    return _base(f"ℹ️ {title}" if title else title, description, COLOR_INFO)


def warning(title: str, description: str = "") -> discord.Embed:
    return _base(f"⚠️ {title}" if title else title, description, COLOR_WARNING)


def neutral(title: str, description: str = "") -> discord.Embed:
    return _base(title, description, COLOR_NEUTRAL)


# ---------------------------------------------------------------------------
# Permission / hierarchy helpers
# ---------------------------------------------------------------------------
def role_ids_for(member: discord.Member) -> set:
    return {r.id for r in member.roles}


def is_exempt(member: discord.Member, *,
              channels: Sequence[int] = (),
              channel_id: int = 0,
              roles: Sequence[int] = (),
              users: Sequence[int] = ()) -> bool:
    """True when the member/channel is exempt from a rule."""
    if member.bot:
        return True
    if member.id in set(users):
        return True
    if member.guild.owner_id == member.id:
        return True
    if member.guild_permissions.administrator:
        return True
    if roles and (role_ids_for(member) & set(roles)):
        return True
    if channel_id and channel_id in set(channels):
        return True
    return False


def can_act_on(actor: discord.Member, target: discord.Member) -> tuple:
    """(ok, reason) — validate moderation hierarchy for actor → target."""
    if target.bot and target.id != actor.guild.me.id:
        return False, "I can't moderate other bots."
    if target.id == actor.id:
        return False, "You can't target yourself."
    if target.id == target.guild.owner_id:
        return False, "That member owns this server."
    if target.top_role >= actor.top_role and actor.id != target.guild.owner_id:
        return False, "Your role is not high enough to target that member."
    if target.top_role >= target.guild.me.top_role:
        return False, "My role is not high enough to act on that member."
    return True, ""


def bot_can_manage_role(guild: discord.Guild, role: discord.Role) -> bool:
    me = guild.me
    return me.guild_permissions.manage_roles and role < me.top_role


def parse_duration(text: str) -> Optional[int]:
    """Parse '10m', '2h', '1d', '45s', or plain seconds → seconds."""
    m = re.fullmatch(r"\s*(\d+)\s*(s|m|h|d|w)?\s*", text.lower())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2) or "s"
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}[unit]
    return n * mult


def duration_str(seconds: int) -> str:
    return fmt_duration(seconds)
