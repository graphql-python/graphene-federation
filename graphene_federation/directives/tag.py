from typing import Any, Callable

from graphene_directives import directive_decorator

from .utils import is_non_field
from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def tag(
    field: Any = None,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("tag", federation_version=federation_version)
    decorator = directive_decorator(directive)
    return (
        decorator(field=None)(field) if is_non_field(field) else decorator(field=field)
    )
