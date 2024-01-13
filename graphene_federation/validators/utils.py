import re
from typing import Union

from graphene import Field, Interface, NonNull, ObjectType
from graphene.types.definitions import GrapheneObjectType
from graphene.utils.str_converters import to_camel_case
from graphene_directives import Schema
from graphql import GraphQLField, GraphQLNonNull


def clean_combined_brackets(data, bracket_kind) -> list[str]:
    cleaned = []

    filtered = list(filter(lambda x: x != "", data.split(bracket_kind)))

    for index, field in enumerate(filtered):
        if index % 2:
            cleaned.extend([field, bracket_kind])
        else:
            cleaned.append(field)

    if not len(filtered) % 2 == 0:
        cleaned.append(bracket_kind)

    return cleaned


def build_ast(input_str: str, valid_special_chars: str) -> dict:
    fields = input_str.split()
    cleaned_fields = []
    pattern = rf"[^a-zA-Z{valid_special_chars}]+"

    for field in fields:
        if "{" in field and field != "{":
            cleaned_fields.extend(clean_combined_brackets(field, "{"))
        elif "}" in field and field != "}":
            cleaned_fields.extend(clean_combined_brackets(field, "}"))
        elif field == "{" or field == "}":
            cleaned_fields.append(field)
        else:
            cleaned_fields.append(re.sub(pattern, "", field))

    parent = {}
    field_stack = []
    field_level = [parent]
    for index, field in enumerate(cleaned_fields):
        if field == "{":
            field_level.append(field_level[-1][field_stack[-1]])
        elif field == "}":
            field_level.pop()
        else:
            field_stack.append(field)
            field_level[-1][field] = {}
    return parent


def check_fields_exist_on_type(
    field: str,
    type_: Union[ObjectType, Interface, Field, NonNull],
    ignore_fields: list[str],
    entity_types: dict[str, ObjectType],
) -> bool:
    if field in ignore_fields:
        return True

    if isinstance(type_, GraphQLField):
        return check_fields_exist_on_type(
            field,
            type_.type,  # noqa
            ignore_fields,
            entity_types,
        )
    elif isinstance(type_, GraphQLNonNull):
        return check_fields_exist_on_type(
            field, type_.of_type, ignore_fields, entity_types
        )
    elif isinstance(type_, GrapheneObjectType):
        return field in type_.fields
    elif issubclass(type_, ObjectType) or issubclass(type_, Interface):  # noqa
        return field in entity_types.get(type_._meta.name).fields  # noqa

    return False


def evaluate_ast(
    directive_name: str,
    nodes: dict,
    type_: ObjectType,
    ignore_fields: list[str],
    errors: list[str],
    entity_types: dict[str, ObjectType],
) -> None:
    for field, value in nodes.items():
        if not check_fields_exist_on_type(
            field,
            type_,
            ignore_fields,
            entity_types,
        ):
            errors.append(
                f'@{directive_name}, field "{field}" does not exist on type "{type_}"'
            )  # noqa
        if len(value) != 0:
            if hasattr(type_, "_meta"):
                type_ = entity_types.get(type_._meta.name)  # noqa
                field_type = type_.fields[field]  # noqa
            else:
                field_type = type_.fields[field]  # noqa
            evaluate_ast(
                directive_name,
                value,
                field_type,
                ignore_fields,
                errors,
                entity_types,
            )


def to_case(fields: str, schema: Schema) -> str:
    return to_camel_case(fields) if schema.auto_camelcase else fields
