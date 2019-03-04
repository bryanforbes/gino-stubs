from typing import Optional, Union, List
from mypy.plugin import FunctionContext, MethodContext, DynamicClassDefContext
from mypy.nodes import Expression, TupleExpr, RefExpr, TypeInfo
from mypy.types import Type, Instance, TupleType
from mypy.typevars import fill_typevars_with_any

from .utils import (
    create_dynamic_class,
    get_model_from_ctx,
    check_model_values,
    set_declarative,
    lookup_type_info,
)


def declarative_base_hook(ctx: DynamicClassDefContext) -> None:
    cls_bases: List[Instance] = []

    model_classes_arg: Optional[Union[TypeInfo, Expression]] = None
    if 'model_classes' in ctx.call.arg_names:
        model_classes_arg = ctx.call.args[ctx.call.arg_names.index('model_classes')]
    elif len(ctx.call.args) > 1:
        model_classes_arg = ctx.call.args[1]
    else:
        model_classes_arg = lookup_type_info(ctx.api, 'gino.declarative.Model')

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

    model_type_info = lookup_type_info(ctx.api, 'gino.declarative.ModelType')
    info = create_dynamic_class(ctx, cls_bases, metaclass=model_type_info)

    set_declarative(info)


def gino_base_hook(ctx: DynamicClassDefContext) -> None:
    cls_bases: List[Instance] = []

    model_classes_arg: Optional[Union[TypeInfo, Expression]] = None
    if 'model_classes' in ctx.call.arg_names:
        model_classes_arg = ctx.call.args[ctx.call.arg_names.index('model_classes')]
    elif len(ctx.call.args) > 1:
        model_classes_arg = ctx.call.args[1]
    else:
        model_classes_arg = lookup_type_info(ctx.api, 'gino.declarative.Model')

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

    model_type_info = lookup_type_info(ctx.api, 'gino.declarative.ModelType')
    info = create_dynamic_class(
        ctx, cls_bases, metaclass=model_type_info, name=f'{ctx.name}.Model'
    )

    set_declarative(info)


def model_hook(ctx: Union[FunctionContext, MethodContext]) -> Type:
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
