from __future__ import annotations

from abc import abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from disaloud.util import result_reaction, user_name

if TYPE_CHECKING:
    from discord.ext.commands import Context

    from disaloud.bot import Bot

logger = getLogger(__name__)
chatlogger = getLogger(f'{__package__.split(".")[0]}.chat')


class TTSBase(commands.Cog):
    @abstractmethod
    def __init__(self, bot: Bot):
        self.bot = bot

    @abstractmethod
    def is_target(self, message: discord.Message) -> bool:
        """これよんでいい?"""

    @abstractmethod
    async def _join(self, ctx: Context) -> bool:
        """VCに呼び出されたときの初期化"""

    @abstractmethod
    async def _leave(self, ctx: Context | None) -> bool:
        """VCから帰る時の後始末"""

    @abstractmethod
    async def _talk(self, text: str) -> bool:
        """よみあげ"""

    @abstractmethod
    async def _add_text_channel(self, ctx: Context) -> bool:
        """よみあげ対象の追加"""

    # -- commands --
    @commands.command("come", aliases=["c", "join", "j"])
    async def come(self, ctx: Context) -> None:
        ret = await self._join(ctx)
        await result_reaction(ctx, ret)

    @commands.command("add_channel", aliases=["a", "add"])
    async def add_channel(self, ctx: Context) -> None:
        ret = await self._add_text_channel(ctx)
        await result_reaction(ctx, ret)

    @commands.command("bye", aliases=["b"])
    async def bye(self, ctx: Context) -> None:
        ret = await self._leave(ctx)
        await result_reaction(ctx, ret)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """読み上げ OR 空メンションでcome/joinと等価"""
        # TODO プラグイン化
        if (
            message.author == self.bot.user
            or message.author.bot
            or not isinstance(message.channel, discord.TextChannel)
        ):
            return

        # TODO 空メンションをコマンドに割り付けの一般化
        if self.bot.user in message.mentions:
            if (
                message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
                == ""
            ):
                ctx = await self.bot.get_context(message)
                await self.come(ctx)
            return

        # TODO プラグイン化
        if is_target := (
            self.is_target(message) and not message.clean_content.startswith("~~")
        ):
            if message.clean_content.startswith("--"):
                text = message.clean_content.removeprefix("--")
            else:
                text = f"{user_name(message.author)} {message.clean_content}"
            await self._talk(text)
        chatlogger.info(
            "%s %s/%s: %s",
            "⛔✅"[is_target],
            message.guild and message.guild.name,
            user_name(message.author),
            message.clean_content,
        )

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
            await self._leave(None)


async def setup(bot):
    pass
