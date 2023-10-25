# NOTE
# キューに読み上げ対象を積んで、変換結果を逐次再生する設計にすれば複数サーバー対応可能
from __future__ import annotations

from logging import getLogger
from typing import Self, cast

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context

from ...audio import PCMStream
from ...bot import Bot
from ...util import get_voice_channel
from .base import TTSBase

logger = getLogger(__name__)


class TTSGlobalPipe(TTSBase, name="TTS"):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.text_channels: set[discord.abc.MessageableChannel] = set()
        self.audio: PCMStream | None = None
        self.voice_client: discord.VoiceClient | None = None
        # TODO 設定ファイルにするかな?
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(1))

    @staticmethod
    def is_current_guild():
        async def predicate(ctx: Context):
            self = cast(Self, ctx.cog)
            if self.voice_client is None or ctx is None:
                return True
            if self.voice_client.guild == ctx.guild:
                return True
            await ctx.reply("別のサーバーで立ち上がってる")
            return False

        return commands.check(predicate)

    def is_target(self, message: discord.Message) -> bool:
        return message.channel in self.text_channels

    @is_current_guild()
    async def _join(self, ctx: Context) -> bool:
        if not (voice_channel := get_voice_channel(ctx)):
            await ctx.reply("VCに接続してから呼んでください")
            return False

        await self._add_text_channel(ctx)

        if isinstance(ctx.voice_client, discord.VoiceClient):
            if ctx.voice_client.channel == voice_channel:
                return True
            if ctx.voice_client.is_playing():
                logger.info("playing - reset")
                ctx.voice_client.stop()
                self.audio = None
            await ctx.voice_client.disconnect(force=True)
        voice_client = await voice_channel.connect(self_deaf=True)

        self.audio = PCMStream(self.bot.config.input_device)
        voice_client.play(self.audio)
        self.voice_client = voice_client
        return True

    @is_current_guild()
    async def _leave(self, ctx: Context | None) -> bool:
        self.text_channels.clear()

        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect(force=True)
            self.voice_client = None
        if self.audio:
            self.audio = None
        return True

    async def _talk(self, text: str):
        b = self.bot.config.bouyomichan
        url = f'http://{b.host}:{b.port}/talk?text={text.replace(" ", "%20")}'
        try:
            async with self.session.get(url) as response:
                await response.text()
        except (TimeoutError, aiohttp.ClientConnectionError):
            logger.exception("棒読みちゃんが起動していないよ！")

    async def _add_text_channel(self, ctx: Context):
        self.text_channels.add(ctx.channel)


async def setup(bot: Bot):
    await bot.add_cog(TTSGlobalPipe(bot))
