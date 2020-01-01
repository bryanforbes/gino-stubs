import asyncio
from typing import Any, ClassVar, Optional

from sqlalchemy.engine.strategies import EngineStrategy

from .engine import GinoEngine

class GinoStrategy(EngineStrategy):
    name: ClassVar[str] = ...
    engine_cls = GinoEngine
    def create(  # type: ignore
        self,
        name_or_url: str,
        loop: Optional[asyncio.AbstractEventLoop] = ...,
        **kwargs: Any,
    ): ...
