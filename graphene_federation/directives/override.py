from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def override(
    graphene_type,
    from_: str,
    label: str = None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that an object field is now resolved by this subgraph instead of another subgraph where it's also defined.
    This enables you to migrate a field from one subgraph to another.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#override
    """
    directive = get_directive_from_name(
        "override", federation_version=federation_version
    )
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            raise TypeError(
                "\n".join(
                    [
                        f"\nInvalid Usage of {directive}.",
                        "Must be applied on a field level",
                        "Example:",
                        "class Product(graphene.ObjectType)",
                        '\tname = override(graphene.Int(),from="Products")',
                    ]
                )
            )
        return decorator(field=field_or_type, **{"from": from_, "label": label})

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
