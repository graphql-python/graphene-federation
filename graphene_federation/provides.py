from typing import Any, Union

from graphene import Field
from graphene import Schema


def get_provides_parent_types(schema: Schema) -> dict[str, Any]:
    """
    Find all the types for which a field is provided from the schema.
    They can be easily distinguished from the other type as
    the `@provides` decorator used on the type itself adds a `_provide_parent_type` attribute to them.
    """
    provides_parent_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        if getattr(type_.graphene_type, "_provide_parent_type", False):
            provides_parent_types[type_name] = type_.graphene_type
    return provides_parent_types


def provides(field, fields: Union[str, list[str]] = None):
    """

    :param field: base type (when used as decorator) or field of base type
    :param fields:
    :return:
    """
    if fields is None:  # used as decorator on base type
        if isinstance(field, Field):
            raise ValueError("Please specify fields")
        field._provide_parent_type = True
    else:  # used as wrapper over field
        # TODO: We should validate the `fields` input to check it is actually existing fields but we
        # don't have access here to the graphene type of the object it provides those fields for.
        if isinstance(fields, str):
            fields = fields.split()
        field._provides = fields
    return field
