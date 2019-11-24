import sqlalchemy as _sa
from sqlalchemy.sql.elements import (
    BooleanClauseList,
    ClauseElement,
    UnaryExpression,
    ColumnElement,
    TextClause,
    BindParameter,
)
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.sql.expression import Executable
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.engine.url import URL
import asyncio
from .declarative import declared_attr as _gino_declared_attr, Model as _GinoModel
from .schema import GinoSchemaVisitor
from .engine import GinoEngine, StatementType, StatementAndCompiledType, _AcquireContext
from .transaction import GinoTransaction
from . import json_support
from .dialects.base import _IterableCursor
from typing import (
    Any,
    Optional,
    Union,
    Tuple,
    Iterable,
    Mapping,
    Type,
    ClassVar,
    Set,
    TypeVar,
    Generic,
    Generator,
    List,
    overload,
)

_T = TypeVar('_T')
_GE = TypeVar('_GE', bound=GinoExecutor[Any])

class GinoExecutor(Generic[_T]):
    def __init__(self, query: Executable) -> None: ...
    @property
    def query(self) -> Executable: ...
    def model(self: _GE, model: Any) -> _GE: ...
    def return_model(self: _GE, switch: bool) -> _GE: ...
    def timeout(self: _GE, timeout: Optional[int]) -> _GE: ...
    def load(self: _GE, value: Any) -> _GE: ...
    async def all(self, *multiparams: Any, **params: Any) -> List[_T]: ...
    async def first(self, *multiparams: Any, **params: Any) -> Optional[_T]: ...
    async def one_or_none(self, *multiparams: Any, **params: Any) -> Optional[_T]: ...
    async def one(self, *multiparams: Any, **params: Any) -> _T: ...
    async def scalar(self, *multiparams: Any, **params: Any) -> Any: ...
    async def status(self, *multiparams: Any, **params: Any) -> Any: ...
    def iterate(self, *multiparams: Any, **params: Any) -> _IterableCursor[_T]: ...

class _BindContext:
    def __init__(self, *args: Any) -> None: ...
    async def __aenter__(self) -> GinoEngine: ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

class _GinoBind:
    @overload
    def __get__(self, instance: None, owner: Any) -> None: ...
    @overload
    def __get__(self, instance: Gino, owner: Any) -> Optional[GinoEngine]: ...
    def __set__(
        self, instance: Any, value: Optional[Union[GinoEngine, str, URL]]
    ) -> None: ...

class Gino(_sa.MetaData):
    model_base_classes: ClassVar[Tuple[Type[Any], ...]]
    query_executor = GinoEngine
    schema_visitor = GinoSchemaVisitor
    no_delegate: ClassVar[Set[str]]
    bind: _GinoBind  # type: ignore
    def __init__(
        self,
        bind: Optional[GinoEngine] = ...,
        model_classes: Optional[Tuple[Type[Any], ...]] = ...,
        query_ext: bool = ...,
        schema_ext: bool = ...,
        ext: bool = ...,
        reflect: bool = ...,
        schema: Optional[str] = ...,
        quote_schema: Optional[bool] = ...,
        naming_convention: Mapping[Any, Any] = ...,
        info: Optional[Mapping[str, Any]] = ...,
    ) -> None:
        self.declared_attr = _gino_declared_attr

        # from json_support
        self.JSONProperty = json_support.JSONProperty
        self.StringProperty = json_support.StringProperty
        self.DateTimeProperty = json_support.DateTimeProperty
        self.IntegerProperty = json_support.IntegerProperty
        self.BooleanProperty = json_support.BooleanProperty
        self.ObjectProperty = json_support.ObjectProperty
        self.ArrayProperty = json_support.ArrayProperty

        # from sqlalchemy
        self.ARRAY = _sa.ARRAY
        self.BIGINT = _sa.BIGINT
        self.BINARY = _sa.BINARY
        self.BLANK_SCHEMA = _sa.BLANK_SCHEMA
        self.BLOB = _sa.BLOB
        self.BOOLEAN = _sa.BOOLEAN
        self.BigInteger = _sa.BigInteger
        self.Binary = _sa.Binary
        self.Boolean = _sa.Boolean
        self.CHAR = _sa.CHAR
        self.CLOB = _sa.CLOB
        self.CheckConstraint = _sa.CheckConstraint
        self.Column = _sa.Column
        self.ColumnDefault = _sa.ColumnDefault
        self.Constraint = _sa.Constraint
        self.DATE = _sa.DATE
        self.DATETIME = _sa.DATETIME
        self.DDL = _sa.DDL
        self.DECIMAL = _sa.DECIMAL
        self.Date = _sa.Date
        self.DateTime = _sa.DateTime
        self.DefaultClause = _sa.DefaultClause
        self.Enum = _sa.Enum
        self.FLOAT = _sa.FLOAT
        self.FetchedValue = _sa.FetchedValue
        self.Float = _sa.Float
        self.ForeignKey = _sa.ForeignKey
        self.ForeignKeyConstraint = _sa.ForeignKeyConstraint
        self.INT = _sa.INT
        self.INTEGER = _sa.INTEGER
        self.Index = _sa.Index
        self.Integer = _sa.Integer
        self.Interval = _sa.Interval
        self.JSON = _sa.JSON
        self.LargeBinary = _sa.LargeBinary
        self.MetaData = _sa.MetaData
        self.NCHAR = _sa.NCHAR
        self.NUMERIC = _sa.NUMERIC
        self.NVARCHAR = _sa.NVARCHAR
        self.Numeric = _sa.Numeric
        self.PassiveDefault = _sa.PassiveDefault
        self.PickleType = _sa.PickleType
        self.PrimaryKeyConstraint = _sa.PrimaryKeyConstraint
        self.REAL = _sa.REAL
        self.SMALLINT = _sa.SMALLINT
        self.Sequence = _sa.Sequence
        self.SmallInteger = _sa.SmallInteger
        self.String = _sa.String
        self.TEXT = _sa.TEXT
        self.TIME = _sa.TIME
        self.TIMESTAMP = _sa.TIMESTAMP
        self.Table = _sa.Table
        self.Text = _sa.Text
        self.ThreadLocalMetaData = _sa.ThreadLocalMetaData
        self.Time = _sa.Time
        self.TypeDecorator = _sa.TypeDecorator
        self.Unicode = _sa.Unicode
        self.UnicodeText = _sa.UnicodeText
        self.UniqueConstraint = _sa.UniqueConstraint
        self.VARBINARY = _sa.VARBINARY
        self.VARCHAR = _sa.VARCHAR
        self.text = _sa.text
        self.alias = _sa.alias
        self.all_ = _sa.all_
        self.and_ = _sa.and_
        self.asc = _sa.asc
        self.between = _sa.between
        self.bindparam = _sa.bindparam
        self.case = _sa.case
        self.cast = _sa.cast
        self.collate = _sa.collate
        self.column = _sa.column
        self.delete = _sa.delete
        self.desc = _sa.desc
        self.distinct = _sa.distinct
        self.except_ = _sa.except_
        self.except_all = _sa.except_all
        self.exists = _sa.exists
        self.extract = _sa.extract
        self.false = _sa.false
        self.func = _sa.func
        self.funcfilter = _sa.funcfilter
        self.insert = _sa.insert
        self.inspect = _sa.inspect
        self.intersect = _sa.intersect
        self.intersect_all = _sa.intersect_all
        self.join = _sa.join
        self.lateral = _sa.lateral
        self.literal = _sa.literal
        self.literal_column = _sa.literal_column
        self.modifier = _sa.modifier
        self.not_ = _sa.not_
        self.null = _sa.null
        # self.nullsfirst = _sa.nullsfirst
        # self.nullslast = _sa.nullslast
        self.or_ = _sa.or_
        self.outerjoin = _sa.outerjoin
        self.outparam = _sa.outparam
        self.select = _sa.select
        self.subquery = _sa.subquery
        self.table = _sa.table
        self.tablesample = _sa.tablesample
        self.true = _sa.true
        self.tuple_ = _sa.tuple_
        self.type_coerce = _sa.type_coerce
        self.union = _sa.union
        self.union_all = _sa.union_all
        self.update = _sa.update
        self.within_group = _sa.within_group
    @property
    def Model(self) -> Type[_GinoModel]: ...
    async def set_bind(
        self,
        bind: Union[str, URL, GinoEngine],
        loop: Optional[asyncio.AbstractEventLoop] = ...,
        **kwargs: Any,
    ) -> GinoEngine: ...
    def pop_bind(self) -> Optional[GinoEngine]: ...
    def with_bind(
        self, bind: str, loop: Optional[asyncio.AbstractEventLoop] = ..., **kwargs: Any
    ) -> _BindContext: ...
    def __await__(self) -> Generator[Any, None, Gino]: ...
    def compile(
        self, elem: StatementType, *multiparams: Any, **params: Any
    ) -> Tuple[str, Any]: ...
    async def all(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    async def first(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    async def one_or_none(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    async def one(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    async def scalar(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    async def status(
        self, clause: StatementAndCompiledType, *multiparams: Any, **params: Any
    ) -> Any: ...
    def iterate(
        self, clause: Any, *multiparams: Any, **params: Any
    ) -> _IterableCursor[Any]: ...
    def acquire(self, *args: Any, **kwargs: Any) -> _AcquireContext: ...
    def transaction(self, *args: Any, **kwargs: Any) -> GinoTransaction: ...
