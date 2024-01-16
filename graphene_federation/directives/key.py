from typing import Any, Union

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from graphene_federation.validators import InternalNamespace, ast_to_str, build_ast
from .utils import is_non_field


def key(
    fields: Union[str, list[str]],
    resolvable: bool = None,
    *,
    auto_case: bool = True,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Any:
    """
    Designates an object type as an entity and specifies its key fields
    (a set of fields that the subgraph can use to uniquely identify any instance of the entity).

    You can apply multiple @key directives to a single entity (to specify multiple valid sets of key fields)

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#key
    """
    directive = get_directive_from_name("key", federation_version)
    decorator = directive_decorator(directive)
    fields = ast_to_str(
        build_ast(
            fields=fields if isinstance(fields, str) else " ".join(fields),
            directive_name=str(directive),
        )
    )

    if not auto_case:
        fields = f"{InternalNamespace.NO_AUTO_CASE.value} {fields}"

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(
                field=None,
                fields=fields,
                resolvable=resolvable,
            )(field_or_type)
        raise TypeError(
            "\n".join(
                [
                    f"\nInvalid Usage of {directive}.",
                    "Must be applied on a class of ObjectType|InterfaceType",
                    "Example:",
                    f"{directive}",
                    "class Product(graphene.ObjectType)",
                    "\t...",
                ]
            )
        )

    return wrapper
