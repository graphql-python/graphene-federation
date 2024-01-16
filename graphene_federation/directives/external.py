from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def external(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates that this subgraph usually can't resolve a particular object field,
    but it still needs to define that field for other purposes.

    This directive is always used in combination with another directive that references object fields,
    such as @provides or @requires.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#external
    """
    directive = get_directive_from_name("external", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        return decorator(field=field_or_type)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
