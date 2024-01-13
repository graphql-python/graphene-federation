from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema

from .utils import build_ast, evaluate_ast, to_case


def validate_requires(
    parent_type: Union[ObjectType, Interface],
    _field: Field,
    inputs: dict,
    schema: Schema,
) -> bool:
    ast_node = build_ast(
        input_str=to_case(inputs.get("fields"), schema), valid_special_chars='_()"'
    )

    errors = []
    evaluate_ast(
        directive_name="requires",
        nodes=ast_node,
        type_=parent_type.graphene_type,
        ignore_fields=["__typename", "_Typename"],
        errors=errors,
        entity_types=schema.graphql_schema.type_map,
    )
    if len(errors) != 0:
        raise ValueError("\n".join(errors))

    return True
