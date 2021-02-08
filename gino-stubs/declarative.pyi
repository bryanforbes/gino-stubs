from collections import OrderedDict
from typing import Any, Callable
from typing import Dict as TypingDict
from typing import (
    Generic,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from sqlalchemy import Column, Table
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.sql.selectable import FromClause, Join

from .api import Gino
from .schema import GinoSchemaVisitor

_FuncType = Callable[..., Any]
_F = TypeVar('_F', bound=_FuncType)
_T = TypeVar('_T')
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
_MT = TypeVar('_MT', bound=ModelType)

class ColumnAttribute(Generic[_T]):
    prop_name: str
    column: Column[_T]
    def __init__(self, prop_name: str, column: Column[_T]) -> None: ...
    @overload
    def __get__(self, instance: None, owner: Any) -> Column[_T]: ...
    @overload
    def __get__(self, instance: object, owner: Any) -> _T: ...
    def __set__(self, instance: Any, value: _T) -> None: ...
    def __delete__(self, instance: Any) -> None: ...

class InvertDict(TypingDict[_KT, _VT]):
    @overload
    def invert_get(self, key: _VT) -> Optional[_KT]: ...
    @overload
    def invert_get(self, key: _VT, default: Union[_KT, _T]) -> Union[_KT, _T]: ...

class Dict(OrderedDict[_KT, _VT]): ...

class ModelType(type):
    gino: GinoSchemaVisitor
    def _check_abstract(cls) -> None: ...
    def __iter__(cls) -> Iterator[Column[Any]]: ...
    @classmethod
    def __prepare__(
        metacls, __name: str, __bases: Tuple[type, ...], **kwargs: Any
    ) -> Dict[str, Any]: ...
    def __new__(
        metacls: Type[_MT],
        name: str,
        bases: Tuple[type, ...],
        namespace: Any,
        **kwargs: Any,
    ) -> _MT: ...
    def insert(
        cls,
        values: Union[Mapping[Any, Any], Sequence[Any]] = ...,
        inline: bool = ...,
        **kwargs: Any,
    ) -> Insert: ...
    def join(
        cls,
        right: FromClause,
        onclause: Optional[ClauseElement] = ...,
        isouter: bool = ...,
        full: bool = ...,
    ) -> Join: ...
    def outerjoin(
        cls,
        right: FromClause,
        onclause: Optional[ClauseElement] = ...,
        full: bool = ...,
    ) -> Join: ...

@overload
def declared_attr(m: _F) -> _F: ...
@overload
def declared_attr(*, with_table: bool = ...) -> Callable[[_F], _F]: ...

class Model:
    __metadata__: Gino
    __table__: Table
    __attr_factory__: Type[ColumnAttribute[Any]]
    __values__: TypingDict[str, Any]

    _column_name_map: InvertDict[str, str]
    def __init__(self) -> None: ...

def declarative_base(
    metadata: Gino, model_classes: Tuple[Type[Any], ...] = ..., name: str = ...
) -> ModelType: ...
