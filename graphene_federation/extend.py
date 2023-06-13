from typing import Any, Callable, Dict

from graphene import Schema

from graphene_federation.utils import check_fields_exist_on_type, is_valid_compound_key


def get_extended_types(schema: Schema) -> Dict[str, Any]:
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

            # Validation for compound keys
            key_str = " ".join(type_.graphene_type._keys)
            type_name = type_.graphene_type._meta.name
            if "{" in key_str:  # checking for subselection to identify compound key
                assert is_valid_compound_key(
                    type_name, key_str, schema
                ), f'Invalid compound key definition for type "{type_name}"'
    return extended_types


def extend(fields: str) -> Callable:
    """
    Decorator to use to extend a given type.
    The field to extend must be provided as input as a string.
    """

    def decorator(type_):
        assert not hasattr(
            type_, "_keys"
        ), "Can't extend type which is already extended or has @key"
        # Check the provided fields actually exist on the Type.

        if "{" not in fields:  # Check for compound keys
            # Skip valid fields check if the key is a compound key. The validation for compound keys
            # is done on calling get_extended_types()
            fields_set = set(fields.split(" "))
            assert check_fields_exist_on_type(
                fields=fields_set, type_=type_
            ), f'Field "{fields}" does not exist on type "{type_._meta.name}"'

        assert getattr(type_._meta, "description", None) is None, (
            f'Type "{type_.__name__}" has a non empty description and it is also marked with extend.'
            "\nThey are mutually exclusive."
            "\nSee https://github.com/graphql/graphql-js/issues/2385#issuecomment-577997521"
        )
        # Set a `_keys` attribute so it will be registered as an entity
        setattr(type_, "_keys", [fields])
        # Set a `_extended` attribute to be able to distinguish it from the other entities
        setattr(type_, "_extended", True)
        return type_

    return decorator
