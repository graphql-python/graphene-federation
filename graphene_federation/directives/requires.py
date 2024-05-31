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


def requires(
    graphene_type,
    fields: Union[str, list[str]],
    *,
    auto_case: bool = True,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that the resolver for a particular entity field depends on the values of other entity fields
    that are resolved by other subgraphs.

    This tells the router that it needs to fetch the values of those externally defined fields first,
    even if the original client query didn't request them.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#requires
    """
    directive = get_directive_from_name("requires", federation_version)
    decorator = directive_decorator(directive)
    fields = ast_to_str(
        build_ast(
            fields=fields if isinstance(fields, str) else " ".join(fields),
            directive_name=str(directive),
        ),
        add_type_name=True,  # When resolvers receive the data, it will be type-casted as __typename info is added
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
                        "\tid = graphene.ID()",
                        "\torders = graphene.List(Order)"
                        '\torder_count = requires(graphene.Int(),fields="id orders { id }")',
                    ]
                )
            )
        return decorator(
            field=field_or_type,
            fields=fields,
            auto_case=auto_case,
        )

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
