from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def interface_object(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that an object definition serves as an abstraction of another subgraph's entity interface.

    This abstraction enables a subgraph to automatically contribute fields to all entities that implement
    a particular entity interface.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#interfaceobject
    """

    directive = get_directive_from_name("interfaceObject", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        raise TypeError(
            "\n".join(
                [
                    f"\nInvalid Usage of {directive}.",
                    "Must be applied on a class of ObjectType",
                    "Example:",
                    f"{directive}",
                    "class Product(graphene.ObjectType)",
                    "\t...",
                ]
            )
        )

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
