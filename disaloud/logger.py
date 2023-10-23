from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

import discord


def setup_logging(
    level=logging.INFO, other_levels: dict[str, int | str] | None = None
) -> None:
    discord.utils.setup_logging(level=level)
    other_levels = other_levels or {}
    for name, lvl in other_levels.items():
        logging.getLogger(name).setLevel(lvl)

    file = logging.handlers.TimedRotatingFileHandler(
        filename=Path("./log/app.log"),
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
    )
    file.setFormatter(formatter)
    logging.getLogger().addHandler(file)
