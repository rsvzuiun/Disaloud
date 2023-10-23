from __future__ import annotations

import tomllib
from pathlib import Path

import pydantic


@pydantic.dataclasses.dataclass
class BouyomiChan:
    host: str
    port: int
    # voice: int
    # speed: int
    # tone: int


@pydantic.dataclasses.dataclass
class Config:
    token: str
    input_device: str
    bouyomichan: BouyomiChan


def load_config() -> Config:
    if not (fp := Path("./config/develop.toml")).exists():
        fp = Path("./config/config.toml")
    with fp.open("rb") as f:
        obj = tomllib.load(f)
    return pydantic.TypeAdapter(Config).validate_python(obj)
