from typing import Any, Callable, Union

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name
from ..validators import build_ast


def add_typename(fields: dict, level: int = 0) -> str:
    new_fields = []
    if level != 0:
        new_fields.append("__typename")
    for field, value in fields.items():
        if "typename" in field.lower():
            continue
        elif len(value) == 0:
            new_fields.append(field)
        else:
            new_fields.extend([field, "{", add_typename(value, level + 1), "}"])

    return " ".join(new_fields)


def requires(
    field: Any,
    fields: Union[str, list[str]],
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name("requires", federation_version)
    fields = add_typename(
        build_ast(
            input_str=fields if isinstance(fields, str) else " ".join(fields),
            valid_special_chars='_()"',
        )
    )
    return directive_decorator(directive)(
        field=field,
        fields=fields,
    )
