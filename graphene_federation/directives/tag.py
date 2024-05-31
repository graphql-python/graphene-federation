from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def tag(
    graphene_type=None,
    *,
    name: str,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    Applies arbitrary string metadata to a schema location.
    Custom tooling can use this metadata during any step of the schema delivery flow,
    including composition, static analysis, and documentation

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/#tag
    """
    directive = get_directive_from_name("tag", federation_version=federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, name=name)(field_or_type)
        return decorator(field=field_or_type, name=name)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
