from typing import Any, Callable

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def extends(
    non_field: Any = None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("extends", federation_version)

    if non_field:
        return directive_decorator(directive)(field=None)(non_field)

    return directive_decorator(directive)
