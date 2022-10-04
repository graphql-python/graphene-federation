from graphene import Schema


def external(field):
    """
    Mark a field as external.
    """
    field._external = True
    return field


def get_external_fields(schema: Schema) -> []:
    """
    Find all the extended types from the schema.
    They can be easily distinguished from the other type as
    the `@external` decorator adds a `_external` attribute to them.
    """
    external_fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_external", False):
                external_fields[type_name] = type_.graphene_type
                continue
    return external_fields
