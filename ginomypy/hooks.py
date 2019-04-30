from typing import Union
from mypy.plugin import FunctionContext, MethodContext, DynamicClassDefContext
from mypy.types import Type

from .utils import (
    create_dynamic_class,
    get_model_from_ctx,
    check_model_values,
    set_declarative,
    get_base_classes_from_arg,
)


def declarative_base_hook(ctx: DynamicClassDefContext) -> None:
    base_classes = get_base_classes_from_arg(
        ctx, 'model_classes', 'gino.declarative.Model'
    )
    info = create_dynamic_class(
        ctx, base_classes, metaclass='gino.declarative.ModelType'
    )

    set_declarative(info)


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


def model_init_hook(ctx: Union[FunctionContext, MethodContext]) -> Type:
    model = get_model_from_ctx(ctx)

    if '__init__' in model.names or not model.has_base('gino.crud.CRUDModel'):
        return ctx.default_return_type

    assert len(ctx.arg_names) == 1
    assert len(ctx.arg_types) == 1

    check_model_values(ctx, model, 'values')

    return ctx.default_return_type


def crud_model_values_hook(ctx: MethodContext) -> Type:
    model = get_model_from_ctx(ctx)
    check_model_values(ctx, model, 'values')

    return ctx.default_return_type
