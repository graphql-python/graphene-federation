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


class InternalNamespace(Enum):
    UNION = "__union__"
    ARG = "__arg__"


def check_fields_exist_on_type(
    field: str,
    type_: Union[ObjectType, Interface, Field, NonNull],
    ignore_fields: list[str],
    entity_types: dict[str, ObjectType],
) -> Union[GraphQLType, GraphQLField, bool]:
    if field in ignore_fields or field.startswith(
        "__arg__"  # todo handle argument validations
    ):
        return True

    if isinstance(type_, GraphQLField):
        return check_fields_exist_on_type(
            field,
            type_.type,  # noqa
            ignore_fields,
            entity_types,
        )
    if isinstance(type_, GraphQLNonNull):
        return check_fields_exist_on_type(
            field, type_.of_type, ignore_fields, entity_types
        )
    if isinstance(type_, GrapheneObjectType):
        if field in type_.fields:
            return type_.fields[field]
    if isinstance(type_, GraphQLList):
        return check_fields_exist_on_type(
            field, type_.of_type, ignore_fields, entity_types
        )
    if isinstance(type_, GrapheneUnionType):
        for union_type in type_.types:
            if union_type.name.lower() == field.lower():
                return union_type
    try:
        if issubclass(type_, ObjectType) or issubclass(type_, Interface):  # noqa
            entity_fields = entity_types.get(type_._meta.name)  # noqa
            if entity_fields is not None:
                entity_fields = entity_fields.fields  # noqa
                if field in entity_fields:
                    return entity_fields[field]
    except TypeError:
        return False

    return False


def get_type_for_field(
    type_,
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
    Returns the type,is_selectable
    """
    if isinstance(type_, GraphQLField):
        return get_type_for_field(type_.type)
    if isinstance(type_, GraphQLNonNull):
        return get_type_for_field(type_.of_type)
    if isinstance(type_, GraphQLList):
        return get_type_for_field(type_.of_type)
    if (
        isinstance(type_, GrapheneObjectType)
        or isinstance(type_, GrapheneInterfaceType)
        or isinstance(type_, GrapheneUnionType)
    ):
        return type_, True
    if isinstance(type_, GraphQLScalarType) or isinstance(type_, GrapheneEnumType):
        return type_, False

    raise NotImplementedError("get_type_for_field", type_)


""""
AST FUNCTIONS 

For FieldSet Parsing
"""


def _tokenize(input_string):
    input_string = input_string.strip()
    tokens = []
    current_token = ""
    open_braces_count = 0

    if input_string.startswith("{"):
        raise ValueError("@requires cannot start with {")

    index = 0
    while index < len(input_string):
        char = input_string[index]
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
            while index < len(input_string):
                char = input_string[index]
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
                        f"@requires({input_string}) has unknown character {char} at argument {current_token}"
                    )
                index += 1
            if mismatched_parenthesis:
                raise ValueError(
                    f"@requires({input_string}) has mismatched parenthesis"
                )
        elif char == ")":
            raise ValueError(f"@requires({input_string}) has mismatched parenthesis")
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
        raise ValueError(f"@requires({input_string}) has mismatched brackets")

    return tokens


def evaluate_ast(
    directive_name: str,
    nodes: dict,
    type_: ObjectType,
    ignore_fields: list[str],
    errors: list[str],
    entity_types: dict[str, ObjectType],
) -> None:
    for field_name, value in nodes.items():
        field_type = check_fields_exist_on_type(
            field_name,
            type_,
            ignore_fields,
            entity_types,
        )
        has_selections = len(value) != 0

        if not field_type:
            errors.append(
                f'@{directive_name}, field "{field_name}" does not exist on type "{type_}"'
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
                f'@{directive_name}, type {type_}, field "{field_name}" needs sub selections.'
            )
            continue

        if not is_selectable and has_selections:
            errors.append(
                f'@{directive_name}, type {type_}, field "{field_name}" cannot have sub selections.'
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


def build_ast(input_str: str) -> dict:
    cleaned_fields = _tokenize(input_str)

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


def to_case(fields: Union[str, None], schema: Schema) -> str:
    if not fields:
        return ""

    skip_next = False

    if schema.auto_camelcase:
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
