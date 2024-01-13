from typing import Callable

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def key(
    fields: str,
    resolvable: bool = None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("key", federation_version)
    return directive_decorator(directive)(fields=fields, resolvable=resolvable)
