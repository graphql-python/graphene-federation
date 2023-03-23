from graphene import Schema

from graphene_federation.utils import get_attributed_fields


def tag(field, name: str):
    """
    Decorator to use to override a given type.
    """
    field._tag = name
    return field


def get_tagged_fields(schema: Schema) -> dict:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@external` decorator adds a `_external` attribute to them.
    """
    return get_attributed_fields(attribute="_tag", schema=schema)
