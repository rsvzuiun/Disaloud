from __future__ import annotations

import discord
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


async def result_reaction(ctx: commands.Context, result: bool):
    await ctx.message.add_reaction("❌✅"[result])
