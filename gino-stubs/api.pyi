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
)

_T = TypeVar('_T')
_CM = TypeVar('_CM', bound=GinoExecutor)

class GinoExecutor(Generic[_T]):
    def __init__(self, query: Executable) -> None: ...
    @property
    def query(self) -> Executable: ...
    def model(self: _CM, model: Any) -> _CM: ...
    def return_model(self: _CM, switch: bool) -> _CM: ...
    def timeout(self: _CM, timeout: Optional[int]) -> _CM: ...
    def load(self: _CM, value: Any) -> _CM: ...
    async def all(self, *multiparams: Any, **params: Any) -> List[_T]: ...
    async def first(self, *multiparams: Any, **params: Any) -> Optional[_T]: ...
    async def scalar(self, *multiparams: Any, **params: Any) -> Any: ...
    async def status(self, *multiparams: Any, **params: Any) -> Any: ...
    def iterate(self, *multiparams: Any, **params: Any) -> _IterableCursor[_T]: ...

class _BindContext:
    def __init__(self, *args: Any) -> None: ...
    async def __aenter__(self) -> GinoEngine: ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

class Gino(sa.MetaData):
    model_base_classes: ClassVar[Tuple[Type[Any], ...]]
    query_executor = GinoEngine
    schema_visitor = GinoSchemaVisitor
    no_delegate: ClassVar[Set[str]]
    declared_attr = gino_declared_attr
    bind: GinoEngine
    def __init__(
        self,
        bind: Optional[GinoEngine] = ...,
        model_classes: Optional[Tuple[Type[Any], ...]] = ...,
        query_ext: bool = ...,
        schema_ext: bool = ...,
        ext: bool = ...,
        **kwargs: Any,
    ) -> None: ...
    @property
    def Model(self) -> Type[GinoModel]: ...
    async def set_bind(
        self, bind: str, loop: Optional[asyncio.AbstractEventLoop] = ..., **kwargs: Any
    ) -> GinoEngine: ...
    def pop_bind(self) -> Optional[GinoEngine]: ...
    def with_bind(
        self,
        bind: GinoEngine,
        loop: Optional[asyncio.AbstractEventLoop] = ...,
        **kwargs: Any,
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
    # from json_support
    JSONProperty = json_support.JSONProperty
    StringProperty = json_support.StringProperty
    DateTimeProperty = json_support.DateTimeProperty
    IntegerProperty = json_support.IntegerProperty
    BooleanProperty = json_support.BooleanProperty
    ObjectProperty = json_support.ObjectProperty
    ArrayProperty = json_support.ArrayProperty

    # from sqlalchemy
    ARRAY = sa.ARRAY
    BIGINT = sa.BIGINT
    BINARY = sa.BINARY
    BLANK_SCHEMA: Any
    BLOB = sa.BLOB
    BOOLEAN = sa.BOOLEAN
    BigInteger = sa.BigInteger
    Binary = sa.Binary
    Boolean = sa.Boolean
    CHAR = sa.CHAR
    CLOB = sa.CLOB
    CheckConstraint = sa.CheckConstraint
    Column = sa.Column
    ColumnDefault = sa.ColumnDefault
    Constraint = sa.Constraint
    DATE = sa.DATE
    DATETIME = sa.DATETIME
    DDL = sa.DDL
    DECIMAL = sa.DECIMAL
    Date = sa.Date
    DateTime = sa.DateTime
    DefaultClause = sa.DefaultClause
    Enum = sa.Enum
    FLOAT = sa.FLOAT
    FetchedValue = sa.FetchedValue
    Float = sa.Float
    ForeignKey = sa.ForeignKey
    ForeignKeyConstraint = sa.ForeignKeyConstraint
    INT = sa.INT
    INTEGER = sa.INTEGER
    Index = sa.Index
    Integer = sa.Integer
    Interval = sa.Interval
    JSON = sa.JSON
    LargeBinary = sa.LargeBinary
    MetaData = sa.MetaData
    NCHAR = sa.NCHAR
    NUMERIC = sa.NUMERIC
    NVARCHAR = sa.NVARCHAR
    Numeric = sa.Numeric
    PassiveDefault = sa.PassiveDefault
    PickleType = sa.PickleType
    PrimaryKeyConstraint = sa.PrimaryKeyConstraint
    REAL = sa.REAL
    SMALLINT = sa.SMALLINT
    Sequence = sa.Sequence
    SmallInteger = sa.SmallInteger
    String = sa.String
    TEXT = sa.TEXT
    TIME = sa.TIME
    TIMESTAMP = sa.TIMESTAMP
    Table = sa.Table
    Text = sa.Text
    ThreadLocalMetaData = sa.ThreadLocalMetaData
    Time = sa.Time
    TypeDecorator = sa.TypeDecorator
    Unicode = sa.Unicode
    UnicodeText = sa.UnicodeText
    UniqueConstraint = sa.UniqueConstraint
    VARBINARY = sa.VARBINARY
    VARCHAR = sa.VARCHAR

    alias = sa.alias
    all_ = sa.all_
    @classmethod
    def and_(cls, *clauses: ClauseElement) -> BooleanClauseList: ...
    @classmethod
    def asc(cls, column: ColumnElement[Any]) -> UnaryExpression[None]: ...
    between = sa.between
    bindparam = sa.bindparam
    case = sa.case
    cast = sa.cast
    collate = sa.collate
    column = sa.column
    delete = sa.delete
    @classmethod
    def desc(cls, column: ColumnElement[Any]) -> UnaryExpression[None]: ...
    @classmethod
    def distinct(cls, column: ColumnElement[_T]) -> UnaryExpression[_T]: ...
    except_ = sa.except_
    except_all = sa.except_all
    exists = sa.exists
    extract = sa.extract
    false = sa.false
    func = sa.func
    funcfilter = sa.funcfilter
    insert = sa.insert
    inspect = sa.inspect
    intersect = sa.intersect
    intersect_all = sa.intersect_all
    join = sa.join
    lateral = sa.lateral
    literal = sa.literal
    literal_column = sa.literal_column
    modifier = sa.modifier
    not_ = sa.not_
    null = sa.null
    # nullsfirst = sa.nullsfirst
    # nullslast = sa.nullslast
    @classmethod
    def or_(cls, *clauses: ClauseElement) -> BooleanClauseList: ...
    outerjoin = sa.outerjoin
    outparam = sa.outparam
    select = sa.select
    subquery = sa.subquery
    table = sa.table
    tablesample = sa.tablesample
    @classmethod
    def text(
        cls,
        text: str,
        bind: Optional[Union[Engine, Connection]] = ...,
        bindparams: Optional[Iterable[BindParameter[Any]]] = ...,
        typemap: Optional[
            Mapping[str, Union[TypeEngine[Any], Type[TypeEngine[Any]]]]
        ] = ...,
        autocommit: Optional[bool] = ...,
    ) -> TextClause: ...
    true = sa.true
    tuple_ = sa.tuple_
    type_coerce = sa.type_coerce
    union = sa.union
    union_all = sa.union_all
    update = sa.update
    within_group = sa.within_group
