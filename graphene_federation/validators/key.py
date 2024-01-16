from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema

from .utils import build_ast, evaluate_ast, to_case


def validate_key(
    graphene_type: Union[ObjectType, Interface, Field], inputs: dict, schema: Schema
) -> bool:
    """
    Used to validate the inputs and graphene_type of @key
    """
    errors: list[str] = []
    ast_node = build_ast(
        fields=to_case(inputs.get("fields"), schema), directive_name="@key"
    )
    evaluate_ast(
        directive_name="@key",
        ast=ast_node,
        graphene_type=graphene_type,
        ignore_fields=[],
        errors=errors,
        entity_types=schema.graphql_schema.type_map,
    )
    if errors:
        raise ValueError("\n".join(errors))

    return True
