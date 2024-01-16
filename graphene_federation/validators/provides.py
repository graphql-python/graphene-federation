from typing import Union

from graphene import Field, Interface, ObjectType
from graphene_directives import Schema

from .utils import (
    InternalNamespace,
    build_ast,
    evaluate_ast,
    to_case,
)


def validate_provides(
    _parent_type: Union[ObjectType, Interface],
    field: Field,
    inputs: dict,
    schema: Schema,
) -> bool:
    """
    Used to validate the inputs and graphene_type of @provides
    """
    errors: list[str] = []
    auto_case = InternalNamespace.NO_AUTO_CASE.value not in inputs.get("fields", ())
    ast_node = build_ast(
        fields=to_case(inputs.get("fields"), schema, auto_case),
        directive_name="@provides",
    )

    # Get the parent type of the field
    field_parent_type = field
    while hasattr(field_parent_type, "type") or hasattr(field_parent_type, "of_type"):
        if hasattr(field_parent_type, "of_type"):
            field_parent_type = field_parent_type.of_type
        elif hasattr(field_parent_type, "type"):
            field_parent_type = field_parent_type.type
        else:
            raise ValueError(
                f"@provides could not find parent for the field {field} at {_parent_type}"
            )

    evaluate_ast(
        directive_name="@provides",
        ast=ast_node,
        graphene_type=field_parent_type,
        ignore_fields=[
            InternalNamespace.UNION.value,
            InternalNamespace.NO_AUTO_CASE.value,
        ],
        errors=errors,
        entity_types=schema.graphql_schema.type_map,
    )
    if errors:
        raise ValueError("\n".join(errors))

    return True
