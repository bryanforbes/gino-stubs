from typing import TYPE_CHECKING, Optional, Callable
from mypy.plugin import Plugin, FunctionContext, MethodContext
from mypy.types import Type
from sqlmypy import column_hook

if TYPE_CHECKING:
    from typing_extensions import Final  # noqa

COLUMN_NAME = 'sqlalchemy.sql.schema.Column'  # type: Final


class BasicGinoPlugin(Plugin):
    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == COLUMN_NAME:
            return column_hook
        return None

    def get_method_hook(
        self, fullname: str
    ) -> Optional[Callable[[MethodContext], Type]]:
        if fullname == COLUMN_NAME:
            return column_hook
        return None


def plugin(version):
    return BasicGinoPlugin
