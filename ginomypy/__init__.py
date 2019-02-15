from typing import TYPE_CHECKING, Optional, Union, Callable, TypeVar, List
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

        return None

    def get_method_hook(self, fullname: str) -> CBT[MethodContext, Type]:
        if fullname == COLUMN_NAME:
            return column_hook

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


def plugin(version):
    return BasicGinoPlugin
