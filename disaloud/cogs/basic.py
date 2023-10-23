from __future__ import annotations

from logging import getLogger
from typing import cast

import discord
from discord.ext import commands
from discord.ext.commands import Context

from ..bot import Bot
from .tts import TTS

logger = getLogger(__name__)


class Basic(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.tts = cast(TTS, self.bot.get_cog("TTS"))
        if self.tts is None:
            raise ModuleNotFoundError()

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user:
            logger.info(
                "Logged in as %s (ID: %d)", self.bot.user.name, self.bot.user.id
            )

    async def join_command(self, ctx: Context) -> None:
        ret = await self.tts.join(ctx)
        if ret:
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

    @commands.command()
    async def come(self, ctx: Context) -> None:
        await self.join_command(ctx)

    @commands.command()
    async def join(self, ctx: Context) -> None:
        await self.join_command(ctx)

    @commands.command()
    async def bye(self, ctx: Context) -> None:
        await self.tts.leave(ctx)
        await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """空メンションでcome/joinと等価"""
        if (
            message.author == self.bot.user
            or message.author.bot
            or not isinstance(message.channel, discord.TextChannel)
        ):
            return

        if self.bot.user in message.mentions:
            if (
                message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
                == ""
            ):
                ctx = await self.bot.get_context(message)
                return await self.join_command(ctx)
            else:
                return

        self.tts.talk(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.reply("そんなコマンドないです")
            await ctx.message.add_reaction("❌")
            return

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """自動切断 - BOTがひとりぼっちになったら寝る"""
        if (
            member.guild.voice_client
            and before.channel
            and len(before.channel.members) == 1
        ):
            await self.tts.leave(None)


async def setup(bot: Bot):
    await bot.add_cog(Basic(bot))
