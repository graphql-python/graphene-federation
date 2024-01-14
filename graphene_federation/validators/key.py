from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema

from .utils import build_ast, evaluate_ast, to_case


def validate_key(
    type_: Union[ObjectType, Interface, Field], inputs: dict, schema: Schema
) -> bool:
    errors: list[str] = []
    ast_node = build_ast(input_str=to_case(inputs.get("fields"), schema))
    evaluate_ast(
        directive_name="key",
        nodes=ast_node,
        type_=type_,
        ignore_fields=[],
        errors=errors,
        entity_types=schema.graphql_schema.type_map,
    )
    if errors:
        raise ValueError("\n".join(errors))

    return True
