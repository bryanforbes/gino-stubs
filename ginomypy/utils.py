from typing import Optional, Union, List, Dict, Callable
from typing_extensions import Protocol, runtime_checkable
from mypy.mro import calculate_mro, MroError
from mypy.nodes import (
    TypeInfo,
    ClassDef,
    Block,
    SymbolTable,
    SymbolTableNode,
    GDEF,
    MDEF,
    Expression,
    Var,
    TupleExpr,
    RefExpr,
    FuncBase,
    SymbolNode,
)
from mypy.plugin import DynamicClassDefContext, FunctionContext, MethodContext
from mypy.types import Instance, Type, TupleType, UnionType, NoneTyp
from mypy.typevars import fill_typevars_with_any

from .names import COLUMN_NAME, JSON_NAMES


try:
    from mypy.types import get_proper_type as _get_proper_type

    get_proper_type = _get_proper_type
except ImportError:
    get_proper_type = lambda x: x  # noqa: E731

# See https://github.com/python/mypy/issues/6617 for plugin API updates.


def get_fullname(x: Union[FuncBase, SymbolNode]) -> str:
    """Compatibility helper for mypy 0.750 vs older."""
    fn: Union[str, Callable[..., str]] = x.fullname
    if callable(fn):
        return fn()
    return fn


def get_shortname(x: Union[FuncBase, SymbolNode]) -> str:
    """Compatibility helper for mypy 0.750 vs older."""
    fn: Union[str, Callable[..., str]] = x.name
    if callable(fn):
        return fn()
    return fn


@runtime_checkable
class FullyQualifiedObject(Protocol):
    def lookup_fully_qualified(self, __name: str) -> Optional[SymbolTableNode]:
        ...


@runtime_checkable
class FullyQualifiedOrNoneObject(Protocol):
    def lookup_fully_qualified_or_none(self, __name: str) -> Optional[SymbolTableNode]:
        ...


def is_declarative(info: TypeInfo) -> bool:
    if info.mro:
        for base in info.mro:
            metadata = base.metadata.get('gino')
            if metadata and metadata.get('declarative_base'):
                return True

    return False


def set_declarative(info: TypeInfo) -> None:
    info.metadata.setdefault('gino', {})['declarative_base'] = True


def set_patched(info: TypeInfo) -> None:
    info.metadata.setdefault('gino', {})['patched'] = True


def is_patched(info: TypeInfo, key: str) -> bool:
    return info.metadata.get('gino', {}).get('patched', False)


def lookup_type_info(
    obj: Union[FullyQualifiedObject, FullyQualifiedOrNoneObject], fullname: str
) -> Optional[TypeInfo]:
    if isinstance(obj, FullyQualifiedOrNoneObject):
        sym = obj.lookup_fully_qualified_or_none(fullname)
    else:
        sym = obj.lookup_fully_qualified(fullname)

    if sym and isinstance(sym.node, TypeInfo):
        return sym.node

    return None


def add_var_to_class(info: TypeInfo, name: str, typ: Type) -> None:
    var = Var(name)
    var.info = info
    var._fullname = get_fullname(info) + '.' + name
    var.type = typ
    info.names[name] = SymbolTableNode(MDEF, var)


def add_metadata(ctx: DynamicClassDefContext, info: TypeInfo) -> None:
    assert len(ctx.call.args) >= 1
    metadata = ctx.call.args[0]

    assert isinstance(metadata, RefExpr) and isinstance(metadata.node, Var)
    typ = Instance(metadata.node.info, [])
    add_var_to_class(info, '__metadata__', typ)


def create_dynamic_class(
    ctx: DynamicClassDefContext,
    bases: List[Instance],
    *,
    name: Optional[str] = None,
    metaclass: Optional[str] = None,
    symbol_table: Optional[SymbolTable] = None,
) -> TypeInfo:
    if name is None:
        name = ctx.name

    class_def = ClassDef(name, Block([]))
    class_def.fullname = ctx.api.qualified_name(name)

    info = TypeInfo(SymbolTable(), class_def, ctx.api.cur_mod_id)

    if metaclass is not None:
        metaclass_type_info = lookup_type_info(ctx.api, metaclass)
        if metaclass_type_info is not None:
            info.declared_metaclass = Instance(metaclass_type_info, [])

    class_def.info = info

    obj = ctx.api.builtin_type('builtins.object')
    info.bases = bases or [obj]

    try:
        calculate_mro(info)
    except MroError:
        ctx.api.fail('Not able to calculate MRO for dynamic class', ctx.call)
        info.bases = [obj]
        info.fallback_to_any = True

    if symbol_table is None:
        ctx.api.add_symbol_table_node(name, SymbolTableNode(GDEF, info))
    else:
        symbol_table[name] = SymbolTableNode(GDEF, info)

    return info


def get_model_from_ctx(ctx: Union[FunctionContext, MethodContext]) -> TypeInfo:
    assert isinstance(ctx.default_return_type, Instance)
    model = ctx.default_return_type.type

    if get_fullname(model) == 'typing.Coroutine':
        assert isinstance(ctx.default_return_type.args[2], Instance)
        model = ctx.default_return_type.args[2].type

    if not model.has_base('gino.crud.CRUDModel'):
        args = ctx.default_return_type.args
        if (
            len(args) > 0
            and isinstance(args[0], Instance)
            and args[0].type.has_base('gino.crud.CRUDModel')
        ):
            model = args[0].type

    return model


def get_expected_model_types(model: TypeInfo) -> Dict[str, Type]:
    expected_types: Dict[str, Type] = {}

    for name, sym in model.names.items():
        if isinstance(sym.node, Var):
            tp = get_proper_type(sym.node.type)
            if isinstance(tp, Instance):
                fullname = get_fullname(tp.type)
                if fullname == COLUMN_NAME:
                    assert len(tp.args) == 1
                    expected_types[name] = tp.args[0]
                elif fullname in JSON_NAMES:
                    expected_types[name] = UnionType(
                        [tp.type.bases[0].args[0], NoneTyp()]
                    )

    return expected_types


def get_base_classes_from_arg(
    ctx: DynamicClassDefContext, arg_name: str, default_value: str
) -> List[Instance]:
    base_classes: List[Instance] = []

    arg: Optional[Union[TypeInfo, Expression]] = None
    if arg_name in ctx.call.arg_names:
        arg = ctx.call.args[ctx.call.arg_names.index(arg_name)]
    elif len(ctx.call.args) > 1:
        arg = ctx.call.args[1]
    else:
        arg = lookup_type_info(ctx.api, default_value)

    if arg is not None:
        if isinstance(arg, TupleExpr):
            items: List[Union[Expression, TypeInfo]] = [item for item in arg.items]
        else:
            items = [arg]

        for item in items:
            base: Optional[Union[Instance, TupleType]] = None
            if isinstance(item, RefExpr) and isinstance(item.node, TypeInfo):
                base = fill_typevars_with_any(item.node)
            elif isinstance(item, TypeInfo):
                base = fill_typevars_with_any(item)

            if isinstance(base, Instance):
                base_classes.append(base)

    return base_classes


def check_model_values(
    ctx: Union[MethodContext, FunctionContext], model: TypeInfo, arg_name: str
) -> None:
    arg_index = ctx.callee_arg_names.index('values')
    expected_types = get_expected_model_types(model)

    for actual_name, actual_type in zip(
        ctx.arg_names[arg_index], ctx.arg_types[arg_index]
    ):
        if actual_name is None:
            continue

        if actual_name not in expected_types:
            ctx.api.fail(
                f'Unexpected argument "{actual_name}"'.format(
                    actual_name, get_shortname(model)
                ),
                ctx.context,
            )
            continue

        # Using private API to simplify life.
        ctx.api.check_subtype(  # type: ignore
            actual_type,
            expected_types[actual_name],
            ctx.context,
            f'Incompatible type for argument "{actual_name}"',
            'got',
            'expected',
        )


def get_argument_by_name(ctx: FunctionContext, name: str) -> Optional[Expression]:
    """Return the expression for the specific argument.
    This helper should only be used with non-star arguments.
    """
    if name not in ctx.callee_arg_names:
        return None
    idx = ctx.callee_arg_names.index(name)
    args = ctx.args[idx]
    if len(args) != 1:
        # Either an error or no value passed.
        return None
    return args[0]
