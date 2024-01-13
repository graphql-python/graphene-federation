from graphene.utils.str_converters import to_camel_case
from graphene_directives import Schema


def field_set_case_transform(inputs: dict, schema: Schema) -> dict:
    fields = inputs.get("fields")
    if fields:
        inputs["fields"] = (
            to_camel_case(fields).replace("_Typename", "__typename")
            if schema.auto_camelcase
            else fields
        )
    return inputs
