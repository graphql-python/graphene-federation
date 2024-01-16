from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def shareable(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that an object type's field is allowed to be resolved by multiple subgraphs
    (by default in Federation 2, object fields can be resolved by only one subgraph).

    If applied to an object type definition, all of that type's fields are considered @shareable

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#shareable
    """

    directive = get_directive_from_name(
        "shareable", federation_version=federation_version
    )
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        return decorator(field=field_or_type)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
