from __future__ import annotations

from logging import getLogger

from discord.ext import commands
from discord.ext.commands import Context

from ..bot import Bot
from ..util import result_reaction

logger = getLogger(__name__)


class Basic(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user:
            logger.info(
                "Logged in as %s (ID: %d)", self.bot.user.name, self.bot.user.id
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.reply("そんなコマンドないです")
            await result_reaction(ctx, False)
            return

    @commands.command("reload", aliases=["r"])
    async def reload(self, ctx: Context):
        await self.bot.reload()
        await result_reaction(ctx, True)


async def setup(bot: Bot):
    await bot.add_cog(Basic(bot))
