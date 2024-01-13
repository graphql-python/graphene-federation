from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema
from graphene_directives.utils import has_non_field_attribute


# todoo: remove
def validate_extends(
    type_: Union[ObjectType, Interface, Field], _inputs: dict, _schema: Schema
) -> bool:
    from ..appolo_versions import LATEST_VERSION, get_directive_from_name

    key = get_directive_from_name("key", LATEST_VERSION)

    assert not has_non_field_attribute(
        type_=type_, target_directive=key
    ), f"Can't extend type on {type_} which has @key"

    assert getattr(type_._meta, "description", None) is None, (
        f'Type "{type_.__name__}" has a non empty description and it is also marked with extend.'
        "\nThey are mutually exclusive."
        "\nSee https://github.com/graphql/graphql-js/issues/2385#issuecomment-577997521"
    )

    return True
