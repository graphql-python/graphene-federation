from typing import Union

from graphene import Schema


def requires(field, fields: Union[str, list[str]]):
    """
    Mark the required fields for a given field.
    The input `fields` can be either a string or a list.
    When it is a string we split at spaces to get the list of fields.
    """
    # TODO: We should validate the `fields` input to check it is actually existing fields but we
    # don't have access here to the parent graphene type.
    if isinstance(fields, str):
        fields = fields.split()
    assert not hasattr(
        field, "_requires"
    ), "Can't chain `requires()` method calls on one field."
    field._requires = fields
    return field


def get_required_fields(schema: Schema) -> dict:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@requires` decorator adds a `_requires` attribute to them.
    """
    required_fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_requires", False):
                required_fields[type_name] = type_.graphene_type
                continue
    return required_fields
