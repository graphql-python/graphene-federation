from enum import Enum
from typing import Union

from graphene import Field, Interface, NonNull, ObjectType
from graphene.types.definitions import (
    GrapheneEnumType,
    GrapheneInterfaceType,
    GrapheneObjectType,
    GrapheneScalarType,
    GrapheneUnionType,
)
from graphene.utils.str_converters import to_camel_case
from graphene_directives import Schema
from graphql import (
    GraphQLField,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLType,
)

"""
@requires, @key, @provides 's field is represented internally in a different way

A field definition

"id currency(curreny_value: usd) products{ ... on Bag { id } ... on Cloth { id } }"

is internally represented as

"id currency __arg__(curreny_value: usd) products{ __union__ Bag { id } __union__ Cloth { id } }"
"""


class InternalNamespace(Enum):
    UNION = "__union__"
    ARG = "__arg__"
    NO_AUTO_CASE = "__no_auto_case__"


def check_fields_exist_on_type(
    field: str,
    graphene_type: Union[ObjectType, Interface, Field, NonNull],
    ignore_fields: list[str],
    entity_types: dict[str, ObjectType],
) -> Union[GraphQLType, GraphQLField, bool]:
    """
    Checks if the given field exists on the graphene_type

    :param field: field that needs to be checked for existence
    :param graphene_type: Union[ObjectType, Interface, Field, NonNull]
    :param ignore_fields: fields that can be ignored for checking example __typename
    :param entity_types: A dictionary of [entity_name, graphene_type]
    """
    if field in ignore_fields or field.startswith(
        "__arg__"  # todo handle argument type validations
    ):
        return True

    if isinstance(graphene_type, GraphQLField):
        return check_fields_exist_on_type(
            field,
            graphene_type.type,  # noqa
            ignore_fields,
            entity_types,
        )
    if isinstance(graphene_type, GraphQLNonNull):
        return check_fields_exist_on_type(
            field, graphene_type.of_type, ignore_fields, entity_types
        )
    if isinstance(graphene_type, GrapheneObjectType):
        if field in graphene_type.fields:
            return graphene_type.fields[field]
    if isinstance(graphene_type, GraphQLList):
        return check_fields_exist_on_type(
            field, graphene_type.of_type, ignore_fields, entity_types
        )
    if isinstance(graphene_type, GrapheneUnionType):
        for union_type in graphene_type.types:
            if union_type.name.lower() == field.lower():
                return union_type
    try:
        if issubclass(
            graphene_type,  # noqa
            ObjectType,
        ) or issubclass(
            graphene_type,  # noqa
            Interface,
        ):
            entity_fields = entity_types.get(graphene_type._meta.name)  # noqa
            if entity_fields is not None:
                entity_fields = entity_fields.fields  # noqa
                if field in entity_fields:
                    return entity_fields[field]
    except TypeError:
        return False

    return False


def get_type_for_field(
    graphene_field,
) -> tuple[
    Union[
        GrapheneObjectType,
        GrapheneInterfaceType,
        GrapheneUnionType,
        GrapheneScalarType,
        GrapheneEnumType,
    ],
    bool,
]:
    """
    Finds the base type for a given graphene_field

    Returns the graphene_field_type, is_selectable (indicates whether the type has sub selections)
    """
    if isinstance(graphene_field, GraphQLField):
        return get_type_for_field(graphene_field.type)
    if isinstance(graphene_field, GraphQLNonNull):
        return get_type_for_field(graphene_field.of_type)
    if isinstance(graphene_field, GraphQLList):
        return get_type_for_field(graphene_field.of_type)
    if (
        isinstance(graphene_field, GrapheneObjectType)
        or isinstance(graphene_field, GrapheneInterfaceType)
        or isinstance(graphene_field, GrapheneUnionType)
    ):
        return graphene_field, True
    if isinstance(graphene_field, GraphQLScalarType) or isinstance(
        graphene_field, GrapheneEnumType
    ):
        return graphene_field, False

    raise NotImplementedError("get_type_for_field", graphene_field)


""""
AST FUNCTIONS 

For @key, @provides, @requires FieldSet Parsing
"""


def _tokenize_field_set(fields: str, directive_name: str) -> list[str]:
    """
    Splits the fields string to tokens
    """

    fields = fields.strip()
    tokens = []
    current_token = ""
    open_braces_count = 0

    if fields.startswith("{"):
        raise ValueError(f"{directive_name} cannot start with " + "{")

    index = 0
    while index < len(fields):
        char = fields[index]
        if char.isalnum():
            current_token += char
        elif char == "{":
            if current_token:
                tokens.append(current_token)
            tokens.append(char)
            current_token = ""
            open_braces_count += 1
        elif char == "}":
            if current_token:
                tokens.append(current_token)
            tokens.append(char)
            current_token = ""
            open_braces_count -= 1
        elif char == ",":
            if current_token:
                tokens.append(current_token)
            current_token = ""
        elif char == "_":
            current_token += char
        elif char == "(":
            tokens.append(current_token)
            current_token = f"{char}"
            index += 1
            mismatched_parenthesis = True
            while index < len(fields):
                char = fields[index]
                if char.isalnum() or char == ",":
                    current_token += char
                elif char.isspace():
                    index += 1
                    continue
                elif char == ":":
                    current_token += ": "
                elif char == ")":
                    current_token += char
                    mismatched_parenthesis = False
                    tokens.append(
                        ", ".join(current_token.split(",")).replace("(", "__arg__(")
                    )
                    current_token = ""
                    break
                else:
                    ValueError(
                        f"{directive_name}({fields}) has unknown character {char} at argument {current_token}"
                    )
                index += 1
            if mismatched_parenthesis:
                raise ValueError(
                    f"{directive_name}({fields}) has mismatched parenthesis"
                )
        elif char == ")":
            raise ValueError(f"{directive_name}({fields}) has mismatched parenthesis")
        elif char.isspace():
            if current_token == "on":
                tokens.append("__union__")
            elif current_token:
                tokens.append(current_token)
            current_token = ""
        else:
            if current_token:
                tokens.append(current_token)
            current_token = ""

        index += 1

    if current_token:
        tokens.append(current_token)

    if open_braces_count != 0:
        raise ValueError(f"{directive_name}({fields}) has mismatched brackets")

    return tokens


def evaluate_ast(
    directive_name: str,
    ast: dict,
    graphene_type: ObjectType,
    ignore_fields: list[str],
    errors: list[str],
    entity_types: dict[str, ObjectType],
) -> None:
    """
    Checks if the given AST is valid for the graphene_type

    It recursively checks if the fields at a node exist on the graphene_type
    """
    for field_name, value in ast.items():
        field_type = check_fields_exist_on_type(
            field_name,
            graphene_type,
            ignore_fields,
            entity_types,
        )
        has_selections = len(value) != 0

        if not field_type:
            errors.append(
                f'{directive_name}, field "{field_name}" does not exist on type "{graphene_type}"'
            )
            continue

        field_type, is_selectable = (
            get_type_for_field(field_type)
            if not isinstance(field_type, bool)
            else (
                field_type,
                False,
            )
        )

        if is_selectable and not has_selections:
            errors.append(
                f'{directive_name}, type {graphene_type}, field "{field_name}" needs sub selections.'
            )
            continue

        if not is_selectable and has_selections:
            errors.append(
                f'{directive_name}, type {graphene_type}, field "{field_name}" cannot have sub selections.'
            )
            continue

        if len(value) != 0:
            evaluate_ast(
                directive_name,
                value,
                field_type,
                ignore_fields,
                errors,
                entity_types,
            )


def build_ast(fields: str, directive_name: str) -> dict:
    """
    Converts the fields string to an AST tree

    :param fields: string fields
    :param directive_name: name of the directive
    """
    cleaned_fields = _tokenize_field_set(fields, directive_name)

    parent: dict[str, dict] = {}
    field_stack: list[str] = []
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


def ast_to_str(fields: dict, add_type_name: bool = False, level: int = 0) -> str:
    """
    Converts the AST of fields to the original string

    :param fields: AST of fields
    :param add_type_name: adds __typename to sub ast nodes (for @requires)
    :param level: for internal use only
    """

    new_fields = []
    union_type = False
    if level != 0 and add_type_name:
        new_fields.append("__typename")
    for field, value in fields.items():
        if "typename" in field.lower():
            continue
        if "__union__" in field.lower():
            union_type = True
        elif len(value) == 0:
            new_fields.append(field)
        else:
            inner_fields = [
                field,
                "{",
                ast_to_str(value, add_type_name, level + 1),
                "}",
            ]
            if union_type:
                inner_fields.insert(0, "... on")
            new_fields.extend(inner_fields)

    return " ".join(new_fields)


""""
String Helpers

For Schema Field Casing Parsing
"""


def to_case(fields: Union[str, None], schema: Schema, auto_case: bool = True) -> str:
    """
    Converts field str to correct casing according to the schema.auto_camelcase value
    """
    if not fields:
        return ""

    skip_next = False

    if schema.auto_camelcase and auto_case:
        data_fields = []
        for field in fields.split():
            if field == InternalNamespace.UNION.value:
                data_fields.append(field)
                skip_next = True
            elif field == "__typename":
                data_fields.append(field)
            elif field.startswith(InternalNamespace.ARG.value):
                data_fields.append(field)
            else:
                if skip_next:
                    data_fields.append(field)
                    skip_next = False
                else:
                    data_fields.append(to_camel_case(field))
        return " ".join(data_fields)

    return fields
