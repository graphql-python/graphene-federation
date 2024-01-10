from graphene import Schema
from graphene.types.objecttype import ObjectTypeMeta

from graphene_federation.utils import get_attributed_fields


def external(field):
    """
    Mark a field as external.
    """
    if isinstance(field, ObjectTypeMeta):
        field._external_entity = True
    else:
        field._external = True
    return field


def get_external_fields(schema: Schema) -> dict:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@external` decorator adds a `_external` attribute to them.
    """
    return get_attributed_fields(attribute="_external", schema=schema)


def get_external_object_types(schema: Schema) -> dict:
    """
    Find all the extended object types from the schema.
    They can be easily distinguished from the other type as
    the `@external` decorator adds a `_external_entity` attribute to them.
    """
    fields = {}

    for type_name, type_ in schema.graphql_schema.type_map.items():
        if hasattr(type_, "graphene_type") and hasattr(
            type_.graphene_type, "_external_entity"
        ):
            fields[type_name] = type_

    return fields
