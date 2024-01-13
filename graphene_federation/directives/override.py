from typing import Any, Callable

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def override(
    field: Any,
    from_: str,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name(
        "override", federation_version=federation_version
    )
    return directive_decorator(directive)(field=field, **{"from": from_})
