from graphene import Schema

from graphene_federation.utils import get_attributed_fields


def external(field):
    """
    Mark a field as external.
    """
    field._external = True
    return field


def get_external_fields(schema: Schema) -> dict:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@external` decorator adds a `_external` attribute to them.
    """
    return get_attributed_fields(attribute="_external", schema=schema)
