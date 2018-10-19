from .engine import GinoEngine
from sqlalchemy.engine.strategies import EngineStrategy
from typing import Any, Optional, ClassVar
import asyncio

class GinoStrategy(EngineStrategy):
    name: ClassVar[str] = ...
    engine_cls = GinoEngine
    def create(self, name_or_url: str, loop: Optional[asyncio.AbstractEventLoop] = ..., **kwargs: Any): ...  # type: ignore
