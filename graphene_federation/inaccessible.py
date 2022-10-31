from typing import Callable, Any, Optional

from graphene import Schema, Field
from graphene.types.schema import TypeMap


def get_inaccessible_types(schema: Schema) -> dict[str, Any]:
    """
    Find all the inaccessible types from the schema.
    They can be easily distinguished from the other type as
    the `@inaccessible` decorator adds a `_inaccessible` attribute to them.
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
        # TODO Check the provided fields actually exist on the Type.
        # Set a `_inaccessible` attribute to be able to distinguish it from the other entities
        setattr(Type, "_inaccessible", True)
        return Type

    if field:
        field._inaccessible = True
        return field
    return decorator


def get_inaccessible_fields(schema: Schema) -> dict:
    """
    Find all the inacessible types from the schema.
    They can be easily distinguished from the other type as
    the `@inaccessible` decorator adds a `_inaccessible` attribute to them.
    """
    inaccessible_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_inaccessible", False):
                inaccessible_types[type_name] = type_.graphene_type
                continue
    return inaccessible_types
