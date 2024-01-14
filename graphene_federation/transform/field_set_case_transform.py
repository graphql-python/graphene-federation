from graphene_directives import Schema

from ..validators import InternalNamespace, to_case


def field_set_case_transform(inputs: dict, schema: Schema) -> dict:
    fields = inputs.get("fields")
    if fields:
        inputs["fields"] = (
            to_case(fields, schema)
            .replace(InternalNamespace.UNION.value, "... on")
            .replace(InternalNamespace.ARG.value, "")
        )
    return inputs
