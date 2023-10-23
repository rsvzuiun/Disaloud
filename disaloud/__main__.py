import asyncio
import logging

import discord
from discord.ext import commands

from . import Bot, load_config, setup_logging


async def main():
    conf = load_config()
    setup_logging(logging.INFO, {"discord.http": logging.WARNING})

    intents = discord.Intents.default()
    intents.message_content = True

    presence = discord.Game("unchi!")
    exts = [
        ".cogs.tts",
        ".cogs.basic",
    ]
    async with Bot(
        command_prefix=commands.when_mentioned_or(),
        intents=intents,
        exts=exts,
        activity=presence,
        config=conf,
    ) as bot:
        await bot.start(conf.token)


if __name__ == "__main__":
    asyncio.run(main())
