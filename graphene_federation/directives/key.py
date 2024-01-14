from typing import Any, Union

from graphene_directives import directive_decorator

from .utils import is_non_field
from ..apollo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name
from ..validators import ast_to_str, build_ast


def key(
    fields: Union[str, list[str]],
    resolvable: bool = None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Any:
    directive = get_directive_from_name("key", federation_version)
    decorator = directive_decorator(directive)
    fields = ast_to_str(
        build_ast(
            fields if isinstance(fields, str) else " ".join(fields),
        )
    )

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, fields=fields, resolvable=resolvable)(
                field_or_type
            )
        raise TypeError(
            "\n".join(
                [
                    f"\nInvalid Usage of {directive}.",
                    "Must be applied on a class of ObjectType|InterfaceType",
                    "Example:",
                    f"{directive}",
                    "class Product(graphene.ObjectType)",
                    "\t...",
                ]
            )
        )

    return wrapper
