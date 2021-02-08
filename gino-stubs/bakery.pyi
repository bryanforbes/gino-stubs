from typing import Any, Optional, Type, TypeVar, Union, overload
from typing_extensions import Protocol

from sqlalchemy.sql.base import Executable
from sqlalchemy.sql.elements import TextClause

from .api import GinoExecutor
from .crud import _CM, _GinoSelect
from .declarative import Model

_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)
_E = TypeVar('_E', bound=Executable)
_M = TypeVar('_M', bound=Model)

class BakedQuery(GinoExecutor[_T]):
    def __init__(
        self, elem: Any, metadata: Any, hash_: Optional[int] = ...
    ) -> None: ...
    def get(self, _: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    @property
    def compiled_sql(self) -> Any: ...
    @property
    def sql(self) -> Any: ...
    @property
    def query(self) -> Any: ...
    @property
    def bind(self) -> Any: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: Any) -> bool: ...
    def execution_options(self, **kwargs: Any) -> BakedQuery[_T]: ...

class _ShadowBakedQuery(BakedQuery[_T]):
    _SBQ = TypeVar('_SBQ', bound='_ShadowBakedQuery[_T]')
    def execution_options(self: '_SBQ', **kwargs: Any) -> '_SBQ': ...

class _BakeFunc(Protocol[_T_co]):
    def __call__(self) -> _T_co: ...

class _BakeModelGetter(Protocol[_T_co]):
    def __call__(self, __cls: Type[_M]) -> _T_co: ...

class _BakeDecorator(Protocol):
    @overload
    def __call__(self, __val: _E) -> BakedQuery[_E]: ...
    @overload
    def __call__(self, __val: str) -> BakedQuery[TextClause]: ...
    @overload
    def __call__(
        self, __val: _BakeModelGetter[_GinoSelect[_CM]]
    ) -> BakedQuery[_CM]: ...
    @overload
    def __call__(self, __val: _BakeModelGetter[_T]) -> BakedQuery[_T]: ...
    @overload
    def __call__(self, __val: _BakeFunc[_E]) -> BakedQuery[_E]: ...
    @overload
    def __call__(self, __val: _BakeFunc[str]) -> BakedQuery[TextClause]: ...

class Bakery:
    query_cls: Any
    def __init__(self) -> None: ...
    def __iter__(self) -> Any: ...
    @overload
    def bake(
        self,
        func_or_elem: None = ...,
        **execution_options: Any,
    ) -> _BakeDecorator: ...
    @overload
    def bake(
        self,
        func_or_elem: _E,
        **execution_options: Any,
    ) -> BakedQuery[_E]: ...
    @overload
    def bake(
        self,
        func_or_elem: str,
        **execution_options: Any,
    ) -> BakedQuery[TextClause]: ...
    @overload
    def bake(
        self,
        func_or_elem: _BakeFunc[_E],
        **execution_options: Any,
    ) -> BakedQuery[_E]: ...
    @overload
    def bake(
        self,
        func_or_elem: _BakeFunc[str],
        **execution_options: Any,
    ) -> BakedQuery[TextClause]: ...
