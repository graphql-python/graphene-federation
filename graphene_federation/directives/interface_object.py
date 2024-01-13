from typing import Callable

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def interface_object(
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name(
        "interfaceObject", federation_version=federation_version
    )
    return directive_decorator(directive)
