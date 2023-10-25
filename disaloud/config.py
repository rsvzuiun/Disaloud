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
    use_global_pipe: bool
    bouyomichan: BouyomiChan


def load_config() -> Config:
    if not (fp := Path("./develop.toml")).exists():
        fp = Path("./config.toml")
    with fp.open("rb") as f:
        obj = tomllib.load(f)
    return pydantic.TypeAdapter(Config).validate_python(obj)
