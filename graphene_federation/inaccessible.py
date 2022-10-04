from typing import Callable, Any, Optional

from graphene import Schema, Field
from graphene.types.schema import TypeMap


def get_inaccessible_types(schema: Schema) -> dict[str, Any]:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@extend` decorator adds a `_extended` attribute to them.
    """
    inaccessible_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        if getattr(type_.graphene_type, "_inaccessible", False):
            inaccessible_types[type_name] = type_.graphene_type
    return inaccessible_types


def inaccessible(field: Optional[Any] = None) -> Any:
    """
    Decorator to use to inaccessible a given type.
    """

    # noinspection PyProtectedMember,PyPep8Naming
    def decorator(Type):
        assert not hasattr(
            Type, "_keys"
        ), "Can't extend type which is already extended or has @key"
        # Check the provided fields actually exist on the Type.
        assert getattr(Type._meta, "description", None) is None, (
            f'Type "{Type.__name__}" has a non empty description and it is also marked with extend.'
            "\nThey are mutually exclusive."
            "\nSee https://github.com/graphql/graphql-js/issues/2385#issuecomment-577997521"
        )
        # Set a `_extended` attribute to be able to distinguish it from the other entities
        setattr(Type, "_inaccessible", True)
        return Type

    if field:
        field._inaccessible = True
        return field
    return decorator


def get_inaccessible_fields(schema: Schema) -> []:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@_tag` decorator adds a `_tag` attribute to them.
    """
    shareable_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_inaccessible", False):
                shareable_types[type_name] = type_.graphene_type
                continue
    return shareable_types
