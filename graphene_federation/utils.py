from typing import Any, Callable, List, Tuple

import graphene
from graphene import Schema, ObjectType
from graphene.types.definitions import GrapheneObjectType
from graphene.types.enum import EnumOptions
from graphene.types.scalars import ScalarOptions
from graphene.types.union import UnionOptions
from graphene.utils.str_converters import to_camel_case
from graphql import parse, GraphQLScalarType, GraphQLNonNull


def field_name_to_type_attribute(schema: Schema, model: Any) -> Callable[[str], str]:
    """
    Create field name conversion method (from schema name to actual graphene_type attribute name).
    """
    field_names = {}
    if schema.auto_camelcase:
        field_names = {
            to_camel_case(attr_name): attr_name
            for attr_name in getattr(model._meta, "fields", [])
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
    key_document = parse(f"{{{key}}}")

    # List storing tuples of nodes in the key document with its parent types
    key_nodes: List[Tuple[Any, GrapheneObjectType]] = [
        (key_document.definitions[0], schema.graphql_schema.type_map[type_name])
    ]

    while key_nodes:
        selection_node, parent_object_type = key_nodes[0]
        if isinstance(parent_object_type, GraphQLNonNull):
            parent_type_fields = parent_object_type.of_type.fields
        else:
            parent_type_fields = parent_object_type.fields
        for field in selection_node.selection_set.selections:
            if schema.auto_camelcase:
                field_name = to_camel_case(field.name.value)
            else:
                field_name = field.name.value
            if field_name not in parent_type_fields:
                # Field does not exist on parent
                return False

            field_type = parent_type_fields[field_name].type
            if field.selection_set:
                # If the field has sub-selections, add it to node mappings to check for valid subfields

                if isinstance(field_type, GraphQLScalarType) or (
                    isinstance(field_type, GraphQLNonNull)
                    and isinstance(field_type.of_type, GraphQLScalarType)
                ):
                    # sub-selections are added to a scalar type, key is not valid
                    return False

                key_nodes.append((field, field_type))
            else:
                # If there are no sub-selections for a field, it should be a scalar
                if not isinstance(field_type, GraphQLScalarType) and not (
                    isinstance(field_type, GraphQLNonNull)
                    and isinstance(field_type.of_type, GraphQLScalarType)
                ):
                    return False

        key_nodes.pop(0)  # Remove the current node as it is fully processed

    return True


def get_attributed_fields(attribute: str, schema: Schema):
    fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if (
            not hasattr(type_, "graphene_type")
            or isinstance(type_.graphene_type._meta, UnionOptions)
            or isinstance(type_.graphene_type._meta, ScalarOptions)
            or isinstance(type_.graphene_type._meta, EnumOptions)
        ):
            continue
        for field in list(type_.graphene_type._meta.fields):
            if getattr(getattr(type_.graphene_type, field, None), attribute, False):
                fields[type_name] = type_.graphene_type
                continue
    return fields
