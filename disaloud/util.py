from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands


def user_name(user: discord.User | discord.Member) -> str:
    if isinstance(user, discord.Member):
        return user.nick or user.name
    return user.name


def get_voice_channel(ctx: commands.Context) -> discord.member.VocalGuildChannel | None:
    if (
        isinstance(ctx.author, discord.Member)
        and ctx.author.voice
        and ctx.author.voice.channel
    ):
        return ctx.author.voice.channel
    return None


async def result_reaction(ctx: commands.Context, result: bool):  # noqa: FBT001
    await ctx.message.add_reaction("❌✅"[result])
