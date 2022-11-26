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
    # create a temporary schema by extending the existing schema with a query returning
    # the type to be validated
    temp_schema = extend_schema(
        schema.graphql_schema,
        parse(
            f"""
        extend type Query {{
         _tempExtendedQuery: {type_name}
        }}
        """
        ),
    )

    # validate the return of the temporary query with the types key fields.
    # If no errors are raised, the compound key is valid
    errors = validate(
        temp_schema,
        parse(
            f"""
        {{_tempExtendedQuery
            {{
            {key}
          }}
        }}"""
        ),
    )

    return not bool(errors)


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
