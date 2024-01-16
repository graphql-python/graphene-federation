from graphene_directives import Schema

from graphene_federation.validators import InternalNamespace, to_case


def field_set_case_transform(inputs: dict, schema: Schema) -> dict:
    """
    Transform the fields from internal representation to schema representation

    Internal representation uses
        __union__ for representing ... on
        __arg__ for representing (arg1: value1, arg2: value2)
    """
    fields = inputs.get("fields")
    if fields:
        inputs["fields"] = (
            to_case(fields, schema)
            .replace(InternalNamespace.UNION.value, "... on")
            .replace(InternalNamespace.ARG.value, "")
        )
    return inputs
