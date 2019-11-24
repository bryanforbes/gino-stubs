from typing import (
    Any,
    Optional,
    Union,
    Callable,
    Dict,
    List,
    Generic,
    TypeVar,
    List,
    Mapping,
    overload,
)
import datetime

_T = TypeVar('_T')
_U = TypeVar('_U')
_M = TypeVar('_M', bound=Mapping[str, Any])
_JP = TypeVar('_JP', bound=JSONProperty[Any])

class Hook(Generic[_T]):
    parent: JSONProperty[_T] = ...
    method: Any = ...
    def __init__(self, parent: JSONProperty[_T]) -> None: ...
    def __call__(self, method: Callable[[Any], _U]) -> JSONProperty[_U]: ...
    def call(self, instance: Any, val: _T) -> _T: ...

class JSONProperty(Generic[_T]):
    name: str = ...
    default: Optional[Union[Callable[[_JP], _T], _T]] = ...
    prop_name: str = ...
    expression: Hook[_T] = ...
    after_get: Hook[_T] = ...
    before_set: Hook[_T] = ...
    def __init__(
        self: _JP,
        default: Optional[Union[Callable[[_JP], _T], _T]] = ...,
        prop_name: str = ...,
    ) -> None: ...
    @overload
    def __get__(self, instance: None, owner: Any) -> Any: ...
    @overload
    def __get__(self, instance: object, owner: Any) -> Optional[_T]: ...
    def __set__(self, instance: Any, value: Optional[_T]) -> None: ...
    def __delete__(self, instance: Any) -> None: ...
    def get_profile(self, instance: Any) -> Dict[str, Any]: ...
    def save(self, instance: Any, value: _U = ...) -> _U: ...
    def reload(self, instance: Any) -> None: ...
    def make_expression(self, base_exp: Any) -> Any: ...
    def decode(self, val: Any) -> Any: ...
    def encode(self, val: Any) -> Any: ...
    def __hash__(self) -> int: ...

class StringProperty(JSONProperty[str]):
    def make_expression(self, base_exp: Any) -> Any: ...

class DateTimeProperty(JSONProperty[datetime.datetime]):
    def make_expression(self, base_exp: Any) -> Any: ...
    def decode(self, val: Any) -> Optional[datetime.datetime]: ...
    def encode(self, val: Any) -> Optional[str]: ...

class IntegerProperty(JSONProperty[int]):
    def make_expression(self, base_exp: Any) -> Any: ...
    def decode(self, val: Any) -> Optional[int]: ...
    def encode(self, val: Any) -> Optional[int]: ...

class BooleanProperty(JSONProperty[bool]):
    def make_expression(self, base_exp: Any) -> Any: ...
    def decode(self, val: Any) -> Optional[bool]: ...
    def encode(self, val: Any) -> Optional[bool]: ...

class ObjectProperty(JSONProperty[_M]):
    def decode(self, val: Any) -> Optional[_M]: ...
    def encode(self, val: Any) -> Optional[_M]: ...

class ArrayProperty(JSONProperty[List[_T]]):
    def decode(self, val: Any) -> Optional[List[_T]]: ...
    def encode(self, val: Any) -> Optional[List[_T]]: ...
