from typing import TYPE_CHECKING, Optional, Union, Callable, TypeVar, List, Dict
from mypy.plugin import Plugin, FunctionContext, MethodContext, DynamicClassDefContext
from mypy.mro import calculate_mro, MroError
from mypy.nodes import (
    Expression,
    TupleExpr,
    RefExpr,
    TypeInfo,
    ClassDef,
    Block,
    SymbolTable,
    SymbolTableNode,
    MemberExpr,
    NameExpr,
    CallExpr,
    Var,
    GDEF,
)
from mypy.types import Type, Instance, TupleType
from mypy.typevars import fill_typevars_with_any
from sqlmypy import column_hook  # type: ignore

if TYPE_CHECKING:
    from typing_extensions import Final  # noqa

T = TypeVar('T')
U = TypeVar('U')
CB = Optional[Callable[[T], None]]
CBT = Optional[Callable[[T], U]]

COLUMN_NAME = 'sqlalchemy.sql.schema.Column'  # type: Final
DECLARATIVE_BASE_NAME = 'gino.declarative.declarative_base'  # type: Final
CRUD_CLASS_CREATE_NAME = 'gino.crud._CreateWithoutInstance.__call__'  # type: Final
CRUD_UPDATE_NAME = 'gino.crud._UpdateWithInstance.__call__'  # type: Final
CRUD_UPDATE_REQUEST_NAME = 'gino.crud.UpdateRequest.update'  # type: Final
VALUES_NAMES = {
    CRUD_CLASS_CREATE_NAME,
    CRUD_UPDATE_NAME,
    CRUD_UPDATE_REQUEST_NAME,
}  # type: Final


def is_declarative(info: TypeInfo) -> bool:
    if info.mro:
        for base in info.mro:
            metadata = base.metadata.get('gino')
            if metadata and metadata.get('declarative_base'):
                return True

    return False


def set_declarative(info: TypeInfo) -> None:
    info.metadata.setdefault('gino', {})['declarative_base'] = True


class BasicGinoPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> CBT[FunctionContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook

        sym = self.lookup_fully_qualified(fullname)
        if sym and isinstance(sym.node, TypeInfo):
            # May be a model instantiation
            if is_declarative(sym.node):
                return model_hook

        return None

    def get_method_hook(self, fullname: str) -> CBT[MethodContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook
        if fullname in VALUES_NAMES:
            return crud_model_values_hook

        sym = self.lookup_fully_qualified(fullname)
        if sym and isinstance(sym.node, TypeInfo):
            # May be a model instantiation
            if is_declarative(sym.node):
                return model_hook

        return None

    def get_dynamic_class_hook(self, fullname: str) -> CB[DynamicClassDefContext]:
        if fullname == DECLARATIVE_BASE_NAME:
            return declarative_info_hook

        return None


def declarative_info_hook(ctx: DynamicClassDefContext) -> None:
    cls_bases: List[Instance] = []

    model_classes_arg: Optional[Union[TypeInfo, Expression]] = None
    if 'model_classes' in ctx.call.arg_names:
        model_classes_arg = ctx.call.args[ctx.call.arg_names.index('model_classes')]
    elif len(ctx.call.args) > 1:
        model_classes_arg = ctx.call.args[1]
    else:
        gino_model = ctx.api.lookup_fully_qualified('gino.declarative.Model')
        assert isinstance(gino_model.node, TypeInfo)
        model_classes_arg = gino_model.node

    if model_classes_arg is not None:
        if isinstance(model_classes_arg, TupleExpr):
            items: List[Union[Expression, TypeInfo]] = [
                item for item in model_classes_arg.items
            ]
        else:
            items = [model_classes_arg]

        for item in items:
            base: Optional[Union[Instance, TupleType]] = None
            if isinstance(item, RefExpr) and isinstance(item.node, TypeInfo):
                base = fill_typevars_with_any(item.node)
            elif isinstance(item, TypeInfo):
                base = fill_typevars_with_any(item)

            if isinstance(base, Instance):
                cls_bases.append(base)

    class_def = ClassDef(ctx.name, Block([]))
    class_def.fullname = ctx.api.qualified_name(ctx.name)

    model_type = ctx.api.lookup_fully_qualified('gino.declarative.ModelType')
    assert isinstance(model_type.node, TypeInfo)

    info = TypeInfo(SymbolTable(), class_def, ctx.api.cur_mod_id)
    info.declared_metaclass = Instance(model_type.node, [])

    class_def.info = info

    obj = ctx.api.builtin_type('builtins.object')
    info.bases = cls_bases or [obj]

    try:
        calculate_mro(info)
    except MroError:
        ctx.api.fail('Not able to calculate MRO for declarative base', ctx.call)
        info.bases = [obj]
        info.fallback_to_any = True

    ctx.api.add_symbol_table_node(ctx.name, SymbolTableNode(GDEF, info))
    set_declarative(info)


expected_type_cache: Dict[str, Dict[str, Type]] = {}


def model_hook(ctx: Union[FunctionContext, MethodContext]) -> Type:
    model = get_model_from_ctx(ctx)

    if '__init__' in model.names or not model.has_base('gino.crud.CRUDModel'):
        return ctx.default_return_type

    expected_types = get_expected_model_types(model)

    assert len(ctx.arg_names) == 1
    assert len(ctx.arg_types) == 1

    check_model_values(ctx, model, expected_types, 0)

    return ctx.default_return_type


def crud_model_values_hook(ctx: MethodContext) -> Type:
    model = get_model_from_ctx(ctx)
    expected_types = get_expected_model_types(model)

    idx = ctx.callee_arg_names.index('values')

    check_model_values(ctx, model, expected_types, idx)

    return ctx.default_return_type


def get_model_from_ctx(ctx: Union[FunctionContext, MethodContext]) -> TypeInfo:
    assert isinstance(ctx.default_return_type, Instance)
    model = ctx.default_return_type.type

    if model.fullname() == 'typing.Coroutine':
        assert isinstance(ctx.default_return_type.args[2], Instance)
        model = ctx.default_return_type.args[2].type

    if not model.has_base('gino.crud.CRUDModel'):
        if isinstance(ctx.context, CallExpr) and isinstance(
            ctx.context.callee, MemberExpr
        ):
            callee: MemberExpr = ctx.context.callee
            while isinstance(callee.expr, CallExpr) and isinstance(
                callee.expr.callee, MemberExpr
            ):
                callee = callee.expr.callee

            if (
                isinstance(callee.expr, NameExpr)
                and callee.expr.node is not None
                and isinstance(callee.expr.node, Var)
                and isinstance(callee.expr.node.type, Instance)
            ):
                model = callee.expr.node.type.type

    return model


def get_expected_model_types(model: TypeInfo) -> Dict[str, Type]:
    model_name = model.fullname()

    if model_name in expected_type_cache:
        return expected_type_cache[model_name]

    expected_types: Dict[str, Type] = {}

    for name, sym in model.names.items():
        if isinstance(sym.node, Var) and isinstance(sym.node.type, Instance):
            tp = sym.node.type
            if tp.type.fullname() == COLUMN_NAME:
                assert len(tp.args) == 1
                expected_types[name] = tp.args[0]

    expected_type_cache[model_name] = expected_types

    return expected_types


def check_model_values(
    ctx: Union[MethodContext, FunctionContext],
    model: TypeInfo,
    expected_types: Dict[str, Type],
    arg_index: int,
) -> None:
    for actual_name, actual_type in zip(
        ctx.arg_names[arg_index], ctx.arg_types[arg_index]
    ):
        if actual_name is None:
            continue

        if actual_name not in expected_types:
            ctx.api.fail(
                f'Unexpected argument "{actual_name}"'.format(
                    actual_name, model.name()
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


def plugin(version):
    return BasicGinoPlugin
