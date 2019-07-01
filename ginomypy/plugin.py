from typing import Optional, Callable, TypeVar, List, Tuple
from mypy.plugin import Plugin, FunctionContext, MethodContext, DynamicClassDefContext
from mypy.types import Type
from mypy.nodes import MypyFile
from sqlmypy import column_hook  # type: ignore

from .hooks import model_init_hook, crud_model_values_hook, declarative_base_hook
from .names import COLUMN_NAME, DECLARATIVE_BASE_NAME, VALUES_NAMES
from .utils import is_declarative, lookup_type_info

T = TypeVar('T')
U = TypeVar('U')
CB = Optional[Callable[[T], None]]
CBT = Optional[Callable[[T], U]]


class GinoPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> CBT[FunctionContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook  # type: ignore

        info = lookup_type_info(self, fullname)
        if info is not None:
            # May be a model instantiation
            if is_declarative(info):
                return model_init_hook

        return None

    def get_method_hook(self, fullname: str) -> CBT[MethodContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook  # type: ignore
        if fullname in VALUES_NAMES:
            return crud_model_values_hook

        info = lookup_type_info(self, fullname)
        if info is not None:
            # May be a model instantiation
            if is_declarative(info):
                return model_init_hook

        return None

    def get_dynamic_class_hook(self, fullname: str) -> CB[DynamicClassDefContext]:
        if fullname == DECLARATIVE_BASE_NAME:
            return declarative_base_hook

        return None

    def get_additional_deps(self, file: MypyFile) -> List[Tuple[int, str, int]]:
        if file.fullname() == 'gino.api':
            return [(10, 'gino.crud', -1)]

        return []
