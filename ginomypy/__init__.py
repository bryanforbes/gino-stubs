import sys
from typing import Type
from typing_extensions import Final

from mypy.plugin import Plugin

from .plugin import GinoPlugin

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


__version__: Final[str] = importlib_metadata.version('gino-stubs')


def plugin(version: str) -> Type[Plugin]:
    return GinoPlugin
