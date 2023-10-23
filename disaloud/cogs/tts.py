from __future__ import annotations

import logging

import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context

from ..audio import PCMStream
from ..bot import Bot


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
        self.audio = None
        self.voice_client = None

    async def join(self, ctx: Context) -> bool:
        if not (voice_channel := get_voice_channel(ctx)):
            return False

        self.add_channel(ctx)

        if isinstance(ctx.voice_client, discord.VoiceClient):
            if ctx.voice_client.channel == voice_channel:
                voice_client = ctx.voice_client
            else:
                logging.info("move_to")
                await ctx.voice_client.disconnect()
                voice_client = await voice_channel.connect(self_deaf=True)
        else:
            logging.info("connect")
            voice_client = await voice_channel.connect(self_deaf=True)

        if voice_client.is_playing():
            logging.info("playing - reset")
            voice_client.stop()
            self.audio = None
        self.audio = PCMStream(self.bot.config.input_device)
        voice_client.play(self.audio)
        self.voice_client = voice_client
        return True

    def add_channel(self, ctx: Context):
        self.text_channels.add(ctx.channel)

    async def leave(self):
        self.text_channels.clear()

        if self.voice_client:
            self.voice_client.stop()
            # await self.voice_client.voice_disconnect()
            await self.voice_client.disconnect(force=True)
            self.voice_client = None
        if self.audio:
            self.audio = None

    def talk(self, message: discord.Message):
        is_reading = message.channel in self.text_channels
        logging.info(
            "%s %s: %s",
            "⛔✅"[is_reading],
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
