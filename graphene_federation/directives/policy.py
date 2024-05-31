from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def policy(
    graphene_type=None,
    *,
    policies: list[list[str]],
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Indicates to composition that the target element is restricted based on authorization policies
    that are evaluated in a Rhai script or coprocessor.

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#policy
    """
    directive = get_directive_from_name("policy", federation_version=federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, policies=policies)(field_or_type)
        return decorator(field=field_or_type, policies=policies)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
