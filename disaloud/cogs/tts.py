from __future__ import annotations

from logging import getLogger

import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context

from ..audio import PCMStream
from ..bot import Bot

logger = getLogger(__name__)


def user_name(user: discord.User | discord.Member) -> str:
    if isinstance(user, discord.Member):
        return user.nick or user.name
    return user.name


def get_voice_channel(ctx: Context) -> discord.member.VocalGuildChannel | None:
    if (
        isinstance(ctx.author, discord.Member)
        and ctx.author.voice
        and ctx.author.voice.channel
    ):
        return ctx.author.voice.channel
    return None


class TTS(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.text_channels: set[discord.abc.MessageableChannel] = set()
        self.audio: PCMStream | None = None
        self.voice_client: discord.VoiceClient | None = None

    def is_current_guild(self, ctx: Context | None) -> bool:
        if self.voice_client is None or ctx is None:
            return True
        if self.voice_client.guild == ctx.guild:
            return True
        return False

    async def join(self, ctx: Context) -> bool:
        if not self.is_current_guild(ctx):
            await ctx.reply("別のギルドで立ち上がってる")
            return False
        if not (voice_channel := get_voice_channel(ctx)):
            await ctx.reply("VCに接続してから呼んでください")
            return False

        self.add_channel(ctx)

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

    def add_channel(self, ctx: Context):
        if not self.is_current_guild(ctx):
            return
        self.text_channels.add(ctx.channel)

    async def leave(self, ctx: Context | None):
        if not self.is_current_guild(ctx):
            return
        self.text_channels.clear()

        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect(force=True)
            self.voice_client = None
        if self.audio:
            self.audio = None

    def talk(self, message: discord.Message):
        is_reading = message.channel in self.text_channels
        logger.info(
            "%s %s/%s: %s",
            "⛔✅"[is_reading],
            message.guild and message.guild.name,
            user_name(message.author),
            message.clean_content,
        )

        if is_reading:
            b = self.bot.config.bouyomichan
            name = user_name(message.author)
            text = f"{name} {message.clean_content}"
            requests.get(f"http://{b.host}:{b.port}/talk?text={text}")


async def setup(bot: Bot):
    await bot.add_cog(TTS(bot))
