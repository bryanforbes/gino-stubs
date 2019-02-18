from typing import Optional, Callable, TypeVar
from mypy.plugin import Plugin, FunctionContext, MethodContext, DynamicClassDefContext
from mypy.nodes import TypeInfo
from mypy.types import Type
from sqlmypy import column_hook  # type: ignore

from .hooks import model_hook, crud_model_values_hook, declarative_base_hook
from .names import COLUMN_NAME, DECLARATIVE_BASE_NAME, VALUES_NAMES
from .utils import is_declarative

T = TypeVar('T')
U = TypeVar('U')
CB = Optional[Callable[[T], None]]
CBT = Optional[Callable[[T], U]]


class GinoPlugin(Plugin):
    def get_type_info_from_name(self, fullname: str) -> Optional[TypeInfo]:
        sym = self.lookup_fully_qualified(fullname)
        if sym and isinstance(sym.node, TypeInfo):
            return sym.node

        return None

    def get_function_hook(self, fullname: str) -> CBT[FunctionContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook

        info = self.get_type_info_from_name(fullname)
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

        info = self.get_type_info_from_name(fullname)
        if info is not None:
            # May be a model instantiation
            if is_declarative(info):
                return model_hook

        return None

    def get_dynamic_class_hook(self, fullname: str) -> CB[DynamicClassDefContext]:
        if fullname == DECLARATIVE_BASE_NAME:
            return declarative_base_hook

        return None
