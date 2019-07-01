from typing import Type
from mypy.plugin import Plugin
from .plugin import GinoPlugin


def plugin(version: str) -> Type[Plugin]:
    return GinoPlugin
