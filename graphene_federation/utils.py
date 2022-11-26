from typing import Any, Callable

from graphene import Schema, ObjectType
from graphene.utils.str_converters import to_camel_case
from graphql import extend_schema, parse, validate


def field_name_to_type_attribute(schema: Schema, model: Any) -> Callable[[str], str]:
    """
    Create field name conversion method (from schema name to actual graphene_type attribute name).
    """
    field_names = {}
    if schema.auto_camelcase:
        field_names = {
            to_camel_case(attr_name): attr_name for attr_name in model._meta.fields
        }
    return lambda schema_field_name: field_names.get(
        schema_field_name, schema_field_name
    )


def type_attribute_to_field_name(schema: Schema) -> Callable[[str], str]:
    """
    Create a conversion method to convert from graphene_type attribute name to the schema field name.
    """
    if schema.auto_camelcase:
        return lambda attr_name: to_camel_case(attr_name)
    else:
        return lambda attr_name: attr_name


def check_fields_exist_on_type(fields: set, type_: ObjectType):
    return fields.issubset(set(type_._meta.fields))


def is_valid_compound_key(type_name: str, key: str, schema: Schema):
    key = key.replace("{", " { ").replace(
        "}", " } "
    )  # Add padding spaces to curly braces so that they can be parsed separately while using split()

    tokens = key.split()  # tokens list contains field names as well as curly braces
    types_ = [
        schema.graphql_schema.type_map[type_name]
    ]  # the types_ list is used to track the current graphene type whose fields are present in tokens list

    for index, token in enumerate(tokens):

        if token == "{":
            # On encountering opening braces as the current,
            # the previous token holds the parent type of the following subselection
            parent_type = tokens[index - 1]  # parent type of the subselection
            types_.append(types_[-1].fields[parent_type].type)

        elif token == "}":
            # Once closing brace is encountered, the last parent type in types_ list can be removed
            # as all its subfields are checked already
            types_.pop()

        else:  # Current token is a field.
            try:
                types_[-1].fields[
                    token
                ]  # Check for the existence of the current token in the fields dict of its parent type
            except KeyError:
                return False

    if len(types_) != 1:
        # This works as the check for correct number of opening and closing braces.
        # Only the base type provided by 'type_name' parameter will be present after successful parsing of key.
        return False

    return True


def get_attributed_fields(attribute: str, schema: Schema):
    fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type._meta.fields):
            if getattr(getattr(type_.graphene_type, field), attribute, False):
                fields[type_name] = type_.graphene_type
                continue
    return fields
