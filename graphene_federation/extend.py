from typing import Any, Callable, Union

from graphene import Schema


def get_extended_types(schema: Schema) -> dict[str, Any]:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@extend` decorator adds a `_extended` attribute to them.
    """
    extended_types = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        if getattr(type_.graphene_type, "_extended", False):
            extended_types[type_name] = type_.graphene_type
    return extended_types


def extend(fields: str) -> Callable:
    """
    Decorator to use to extend a given type.
    The field to extend must be provided as input as a string.
    """

    def decorator(Type):
        assert not hasattr(
            Type, "_keys"
        ), "Can't extend type which is already extended or has @key"
        # Check the provided fields actually exist on the Type.
        assert (
                fields in Type._meta.fields
        ), f'Field "{fields}" does not exist on type "{Type._meta.name}"'
        assert getattr(Type._meta, "description", None) is None, (
            f'Type "{Type.__name__}" has a non empty description and it is also marked with extend.'
            "\nThey are mutually exclusive."
            "\nSee https://github.com/graphql/graphql-js/issues/2385#issuecomment-577997521"
        )
        # Set a `_keys` attribute so it will be registered as an entity
        setattr(Type, "_keys", [fields])
        # Set a `_extended` attribute to be able to distinguish it from the other entities
        setattr(Type, "_extended", True)
        return Type

    return decorator







