from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def authenticated(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates to composition that the target element is accessible only to the authenticated supergraph users.
    For more granular access control, see the @requiresScopes directive.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#authenticated
    """
    directive = get_directive_from_name("authenticated", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        return decorator(field=field_or_type)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
