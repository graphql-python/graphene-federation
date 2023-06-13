from typing import List, Union

from graphene import Schema

from graphene_federation.utils import get_attributed_fields


def requires(field, fields: Union[str, List[str]]):
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
    Find all the extended types with required fields from the schema.
    They can be easily distinguished from the other type as
    the `@requires` decorator adds a `_requires` attribute to them.
    """
    return get_attributed_fields(attribute="_requires", schema=schema)
