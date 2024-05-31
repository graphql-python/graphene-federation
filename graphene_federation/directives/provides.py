from typing import Callable
from typing import Union

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from graphene_federation.validators import InternalNamespace, ast_to_str, build_ast
from .utils import is_non_field


def provides(
    graphene_type,
    fields: Union[str, list[str]],
    *,
    auto_case: bool = True,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Specifies a set of entity fields that a subgraph can resolve, but only at a particular schema path
    (at other paths, the subgraph can't resolve those fields).

    If a subgraph can always resolve a particular entity field, do not apply this directive.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#provides
    """

    directive = get_directive_from_name(
        "provides", federation_version=federation_version
    )
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
            raise TypeError(
                "\n".join(
                    [
                        f"\nInvalid Usage of {directive}.",
                        "Must be applied on a field level",
                        "Example:",
                        "class Product(graphene.ObjectType)",
                        '\torders = provides(graphene.List(Order),fields="id")',
                    ]
                )
            )
        return decorator(
            field=field_or_type,
            fields=fields,
        )

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
