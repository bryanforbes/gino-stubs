from typing import Union

from mypy.nodes import TypeInfo
from mypy.plugin import (
    ClassDefContext,
    DynamicClassDefContext,
    FunctionContext,
    MethodContext,
)
from mypy.types import AnyType, Instance, Type, TypeOfAny

from .utils import (
    add_var_to_class,
    check_model_values,
    create_dynamic_class,
    get_base_classes_from_arg,
    get_model_from_ctx,
    set_declarative,
)


def declarative_base_hook(ctx: DynamicClassDefContext) -> None:
    base_classes = get_base_classes_from_arg(
        ctx, 'model_classes', 'gino.declarative.Model'
    )
    info = create_dynamic_class(
        ctx, base_classes, metaclass='gino.declarative.ModelType'
    )

    set_declarative(info)
    # add_metadata(ctx, info)


def model_dynamic_class_hook(ctx: DynamicClassDefContext) -> None:
    base_classes = get_base_classes_from_arg(
        ctx, 'model_classes', 'gino.crud.CRUDModel'
    )
    info = create_dynamic_class(
        ctx,
        base_classes,
        metaclass='gino.declarative.ModelType',
        name=f'__{ctx.name}__Model',
    )

    set_declarative(info)
    # add_metadata(ctx, info)


def model_init_hook(ctx: Union[FunctionContext, MethodContext]) -> Type:
    model = get_model_from_ctx(ctx)

    if '__init__' in model.names or not model.has_base('gino.crud.CRUDModel'):
        return ctx.default_return_type

    assert len(ctx.arg_names) == 1
    assert len(ctx.arg_types) == 1

    check_model_values(ctx, model, 'values')

    return ctx.default_return_type


def model_base_class_hook(ctx: ClassDefContext) -> None:
    table = ctx.api.lookup_fully_qualified_or_none('sqlalchemy.sql.schema.Table')

    if table:
        assert isinstance(table.node, TypeInfo)
        typ: Type = Instance(table.node, [])
    else:
        typ = AnyType(TypeOfAny.special_form)

    add_var_to_class(ctx.cls.info, '__table__', typ)


def crud_model_values_hook(ctx: MethodContext) -> Type:
    model = get_model_from_ctx(ctx)
    check_model_values(ctx, model, 'values')

    return ctx.default_return_type
