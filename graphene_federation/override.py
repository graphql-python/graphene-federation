from graphene import Schema

from graphene_federation.utils import get_attributed_fields


def override(field, from_: str):
    """
    Decorator to use to override a given type.
    """
    field._override = from_
    return field


def get_override_fields(schema: Schema) -> dict:
    """
    Find all the overridden types from the schema.
    They can be easily distinguished from the other type as
    the `@override` decorator adds a `_override` attribute to them.
    """
    return get_attributed_fields(attribute="_override", schema=schema)
