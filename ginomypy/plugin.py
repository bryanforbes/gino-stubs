from typing import Callable, List, Optional, Tuple, TypeVar

from mypy.nodes import MypyFile, TypeInfo
from mypy.plugin import (
    ClassDefContext,
    DynamicClassDefContext,
    FunctionContext,
    MethodContext,
    Plugin,
)
from mypy.types import Type
from sqlmypy import column_hook, grouping_hook

from .hooks import (
    crud_model_values_hook,
    declarative_base_hook,
    model_base_class_hook,
    model_init_hook,
)
from .names import COLUMN_NAME, DECLARATIVE_BASE_NAME, GROUPING_NAME, VALUES_NAMES
from .utils import get_fullname, is_declarative

T = TypeVar('T')
U = TypeVar('U')
CB = Optional[Callable[[T], None]]
CBT = Optional[Callable[[T], U]]


class GinoPlugin(Plugin):
    def __is_declarative(self, fullname: str) -> bool:
        info = self.lookup_fully_qualified(fullname)
        if info and isinstance(info.node, TypeInfo):
            # May be a model instantiation
            return is_declarative(info.node)

        return False

    def get_function_hook(self, fullname: str) -> CBT[FunctionContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook  # type: ignore
        if fullname == GROUPING_NAME:
            return grouping_hook  # type: ignore

        if self.__is_declarative(fullname):
            return model_init_hook

        return None

    def get_method_hook(self, fullname: str) -> CBT[MethodContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook  # type: ignore
        if fullname == GROUPING_NAME:
            return grouping_hook  # type: ignore

        if fullname in VALUES_NAMES:
            return crud_model_values_hook

        if self.__is_declarative(fullname):
            return model_init_hook

        return None

    def get_dynamic_class_hook(self, fullname: str) -> CB[DynamicClassDefContext]:
        if fullname == DECLARATIVE_BASE_NAME:
            return declarative_base_hook

        return None

    def get_base_class_hook(self, fullname: str) -> CB[ClassDefContext]:
        if self.__is_declarative(fullname):
            return model_base_class_hook

        return None

    def get_additional_deps(self, file: MypyFile) -> List[Tuple[int, str, int]]:
        if get_fullname(file) == 'gino.api':
            return [(10, 'gino.crud', -1)]

        return []
