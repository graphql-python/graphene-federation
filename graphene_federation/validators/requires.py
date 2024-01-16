from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema

from .utils import InternalNamespace, build_ast, evaluate_ast, to_case


def validate_requires(
    parent_type: Union[ObjectType, Interface],
    _field: Field,
    inputs: dict,
    schema: Schema,
) -> bool:
    """
    Used to validate the inputs and graphene_type of @requires
    """
    errors: list[str] = []
    ast_node = build_ast(
        fields=to_case(inputs.get("fields"), schema), directive_name="@requires"
    )
    evaluate_ast(
        directive_name="@requires",
        ast=ast_node,
        graphene_type=parent_type,
        ignore_fields=["__typename", InternalNamespace.UNION.value],
        errors=errors,
        entity_types=schema.graphql_schema.type_map,
    )
    if errors:
        raise ValueError("\n".join(errors))

    return True
