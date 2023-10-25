from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from disaloud import config


class Bot(commands.Bot):
    def __init__(self, *args, exts: list[str], config: config.Config, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.exts = exts
        self.config = config

    async def setup_hook(self) -> None:
        for ext in self.exts:
            await self.load_extension(ext, package=__package__)

    async def reload(self) -> None:
        for ext in self.exts:
            await self.reload_extension(ext, package=__package__)
