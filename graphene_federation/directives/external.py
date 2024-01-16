from typing import Callable

from graphene_directives import directive_decorator

from .utils import is_non_field
from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)


def external(
    graphene_type=None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("external", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None)(field_or_type)
        return decorator(field=field_or_type)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
