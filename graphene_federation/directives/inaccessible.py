from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def inaccessible(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that a definition in the subgraph schema should be omitted from the router's API schema,
    even if that definition is also present in other subgraphs.

    This means that the field is not exposed to clients at all.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#inaccessible
    """
    directive = get_directive_from_name("inaccessible", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        return decorator(field=field_or_type)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
