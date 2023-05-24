from typing import Any, Dict, Optional

from graphene import Schema
from graphene.types.interface import InterfaceOptions

from graphene_federation.utils import get_attributed_fields


def get_shareable_types(schema: Schema) -> Dict[str, Any]:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@shareable` decorator adds a `_shareable` attribute to them.
    """
    shareable_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        if type_name == "PageInfo" or getattr(type_.graphene_type, "_shareable", False):
            shareable_types[type_name] = type_.graphene_type
    return shareable_types


def shareable(field: Optional[Any] = None) -> Any:
    """
    Decorator to use to shareable a given type.
    """

    # noinspection PyProtectedMember,PyPep8Naming
    def decorator(type_):
        assert not hasattr(
            type_, "_keys"
        ), "Can't extend type which is already extended or has @key"
        assert not hasattr(
            type_, "_keys"
        ), "Can't extend type which is already extended or has @key"
        # Check the provided fields actually exist on the Type.
        assert getattr(type_._meta, "description", None) is None, (
            f'Type "{type_.__name__}" has a non empty description and it is also marked with extend.'
            "\nThey are mutually exclusive."
            "\nSee https://github.com/graphql/graphql-js/issues/2385#issuecomment-577997521"
        )
        # Set a `_shareable` attribute to be able to distinguish it from the other entities
        setattr(type_, "_shareable", True)
        return type_

    if field:
        assert not isinstance(field._meta, InterfaceOptions), (
            "The @Shareable directive is about indicating when an object field "
            "can be resolved by multiple subgraphs. As interface fields are not "
            "directly resolved (their implementation is), @Shareable is not "
            "meaningful on an interface field and is not allowed (at least since "
            "federation 2.2; earlier versions of federation 2 mistakenly ignored "
            "@Shareable on interface fields). "
        )
        field._shareable = True
        return field
    return decorator


def get_shareable_fields(schema: Schema) -> dict:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@shareable` decorator adds a `_shareable` attribute to them.
    """
    return get_attributed_fields(attribute="_shareable", schema=schema)
