import sqlalchemy as sa
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
from .declarative import declared_attr as gino_declared_attr, Model as GinoModel
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
_GE = TypeVar('_GE', bound=GinoExecutor)

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

class Gino(sa.MetaData):
    model_base_classes: ClassVar[Tuple[Type[Any], ...]]
    query_executor = GinoEngine
    schema_visitor = GinoSchemaVisitor
    no_delegate: ClassVar[Set[str]]
    declared_attr = gino_declared_attr
    bind: _GinoBind  # type: ignore
    def __init__(
        self,
        bind: Optional[GinoEngine] = ...,
        model_classes: Optional[Tuple[Type[Any], ...]] = ...,
        query_ext: bool = ...,
        schema_ext: bool = ...,
        ext: bool = ...,
        **kwargs: Any,
    ) -> None:
        # from json_support
        self.JSONProperty = json_support.JSONProperty
        self.StringProperty = json_support.StringProperty
        self.DateTimeProperty = json_support.DateTimeProperty
        self.IntegerProperty = json_support.IntegerProperty
        self.BooleanProperty = json_support.BooleanProperty
        self.ObjectProperty = json_support.ObjectProperty
        self.ArrayProperty = json_support.ArrayProperty

        # from sqlalchemy
        self.ARRAY = sa.ARRAY
        self.BIGINT = sa.BIGINT
        self.BINARY = sa.BINARY
        self.BLANK_SCHEMA: Any
        self.BLOB = sa.BLOB
        self.BOOLEAN = sa.BOOLEAN
        self.BigInteger = sa.BigInteger
        self.Binary = sa.Binary
        self.Boolean = sa.Boolean
        self.CHAR = sa.CHAR
        self.CLOB = sa.CLOB
        self.CheckConstraint = sa.CheckConstraint
        self.Column = sa.Column
        self.ColumnDefault = sa.ColumnDefault
        self.Constraint = sa.Constraint
        self.DATE = sa.DATE
        self.DATETIME = sa.DATETIME
        self.DDL = sa.DDL
        self.DECIMAL = sa.DECIMAL
        self.Date = sa.Date
        self.DateTime = sa.DateTime
        self.DefaultClause = sa.DefaultClause
        self.Enum = sa.Enum
        self.FLOAT = sa.FLOAT
        self.FetchedValue = sa.FetchedValue
        self.Float = sa.Float
        self.ForeignKey = sa.ForeignKey
        self.ForeignKeyConstraint = sa.ForeignKeyConstraint
        self.INT = sa.INT
        self.INTEGER = sa.INTEGER
        self.Index = sa.Index
        self.Integer = sa.Integer
        self.Interval = sa.Interval
        self.JSON = sa.JSON
        self.LargeBinary = sa.LargeBinary
        self.MetaData = sa.MetaData
        self.NCHAR = sa.NCHAR
        self.NUMERIC = sa.NUMERIC
        self.NVARCHAR = sa.NVARCHAR
        self.Numeric = sa.Numeric
        self.PassiveDefault = sa.PassiveDefault
        self.PickleType = sa.PickleType
        self.PrimaryKeyConstraint = sa.PrimaryKeyConstraint
        self.REAL = sa.REAL
        self.SMALLINT = sa.SMALLINT
        self.Sequence = sa.Sequence
        self.SmallInteger = sa.SmallInteger
        self.String = sa.String
        self.TEXT = sa.TEXT
        self.TIME = sa.TIME
        self.TIMESTAMP = sa.TIMESTAMP
        self.Table = sa.Table
        self.Text = sa.Text
        self.ThreadLocalMetaData = sa.ThreadLocalMetaData
        self.Time = sa.Time
        self.TypeDecorator = sa.TypeDecorator
        self.Unicode = sa.Unicode
        self.UnicodeText = sa.UnicodeText
        self.UniqueConstraint = sa.UniqueConstraint
        self.VARBINARY = sa.VARBINARY
        self.VARCHAR = sa.VARCHAR
        self.text = sa.text
        self.alias = sa.alias
        self.all_ = sa.all_
        self.and_ = sa.and_
        self.asc = sa.asc
        self.between = sa.between
        self.bindparam = sa.bindparam
        self.case = sa.case
        self.cast = sa.cast
        self.collate = sa.collate
        self.column = sa.column
        self.delete = sa.delete
        self.desc = sa.desc
        self.distinct = sa.distinct
        self.except_ = sa.except_
        self.except_all = sa.except_all
        self.exists = sa.exists
        self.extract = sa.extract
        self.false = sa.false
        self.func = sa.func
        self.funcfilter = sa.funcfilter
        self.insert = sa.insert
        self.inspect = sa.inspect
        self.intersect = sa.intersect
        self.intersect_all = sa.intersect_all
        self.join = sa.join
        self.lateral = sa.lateral
        self.literal = sa.literal
        self.literal_column = sa.literal_column
        self.modifier = sa.modifier
        self.not_ = sa.not_
        self.null = sa.null
        # self.nullsfirst = sa.nullsfirst
        # self.nullslast = sa.nullslast
        self.or_ = sa.or_
        self.outerjoin = sa.outerjoin
        self.outparam = sa.outparam
        self.select = sa.select
        self.subquery = sa.subquery
        self.table = sa.table
        self.tablesample = sa.tablesample
        self.true = sa.true
        self.tuple_ = sa.tuple_
        self.type_coerce = sa.type_coerce
        self.union = sa.union
        self.union_all = sa.union_all
        self.update = sa.update
        self.within_group = sa.within_group
    @property
    def Model(self) -> Type[GinoModel]: ...
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
