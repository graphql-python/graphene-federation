from typing import Callable

from graphene_directives import directive_decorator

from .utils import is_non_field
from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)


def override(
    graphene_type,
    from_: str,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
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
        return decorator(field=field_or_type, **{"from": from_})

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
