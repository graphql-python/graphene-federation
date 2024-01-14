from typing import Callable
from typing import Union

from graphene_directives import directive_decorator

from .utils import is_non_field
from ..apollo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name
from ..validators import ast_to_str, build_ast


def provides(
    graphene_type,
    fields: Union[str, list[str]],
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name(
        "provides", federation_version=federation_version
    )
    decorator = directive_decorator(directive)
    fields = ast_to_str(
        build_ast(
            fields if isinstance(fields, str) else " ".join(fields),
        )
    )

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            raise TypeError(
                "\n".join(
                    [
                        f"\nInvalid Usage of {directive}.",
                        "Must be applied on a field level",
                        "Example:",
                        "class Product(graphene.ObjectType)",
                        '\torders = provides(graphene.List(Order),fields="id")',
                    ]
                )
            )
        return decorator(field=field_or_type, fields=fields)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
