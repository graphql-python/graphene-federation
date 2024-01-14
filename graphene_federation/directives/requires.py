from typing import Callable
from typing import Union

from graphene_directives import directive_decorator

from .utils import is_non_field
from ..apollo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name
from ..validators import ast_to_str, build_ast


def requires(
    graphene_type,
    fields: Union[str, list[str]],
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("requires", federation_version)
    decorator = directive_decorator(directive)
    fields = ast_to_str(
        build_ast(
            fields if isinstance(fields, str) else " ".join(fields),
        ),
        add_type_name=True,  # When resolvers receive the data, it will be type-casted as __typename info is added
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
                        "\tid = graphene.ID()",
                        "\torders = graphene.List(Order)"
                        '\torder_count = requires(graphene.Int(),fields="id orders { id }")',
                    ]
                )
            )
        return decorator(field=field_or_type, fields=fields)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
