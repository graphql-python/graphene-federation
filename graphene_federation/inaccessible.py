from typing import Any, Dict, Optional

from graphene import Schema

from graphene_federation.utils import get_attributed_fields


def get_inaccessible_types(schema: Schema) -> Dict[str, Any]:
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
    def decorator(field_or_type):
        # TODO Check the provided fields actually exist on the Type.
        # Set a `_inaccessible` attribute to be able to distinguish it from the other entities
        setattr(field_or_type, "_inaccessible", True)
        return field_or_type

    if field:
        return decorator(field)
    return decorator


def get_inaccessible_fields(schema: Schema) -> dict:
    """
    Find all the inacessible types from the schema.
    They can be easily distinguished from the other type as
    the `@inaccessible` decorator adds a `_inaccessible` attribute to them.
    """
    return get_attributed_fields(attribute="_inaccessible", schema=schema)
