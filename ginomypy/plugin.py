from typing import Optional, Callable, TypeVar
from mypy.plugin import (
    Plugin,
    FunctionContext,
    MethodContext,
    DynamicClassDefContext,
    AnalyzeTypeContext,
)
from mypy.types import Type
from sqlmypy import column_hook  # type: ignore

from .hooks import (
    model_hook,
    crud_model_values_hook,
    declarative_base_hook,
    gino_base_hook,
)
from .names import COLUMN_NAME, DECLARATIVE_BASE_NAME, VALUES_NAMES
from .utils import is_declarative, lookup_type_info

T = TypeVar('T')
U = TypeVar('U')
CB = Optional[Callable[[T], None]]
CBT = Optional[Callable[[T], U]]


class GinoPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> CBT[FunctionContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook

        info = lookup_type_info(self, fullname)
        if info is not None:
            # May be a model instantiation
            if is_declarative(info):
                return model_hook

        return None

    def get_method_hook(self, fullname: str) -> CBT[MethodContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook
        if fullname in VALUES_NAMES:
            return crud_model_values_hook

        info = lookup_type_info(self, fullname)
        if info is not None:
            # May be a model instantiation
            if is_declarative(info):
                return model_hook

        return None

    def get_dynamic_class_hook(self, fullname: str) -> CB[DynamicClassDefContext]:
        if fullname == DECLARATIVE_BASE_NAME:
            return declarative_base_hook
        if fullname == 'gino.api.Gino':
            return gino_base_hook

        return None

    def get_type_analyze_hook(
        self, fullname: str
    ) -> Optional[Callable[[AnalyzeTypeContext], Type]]:
        print(fullname)
        return None
