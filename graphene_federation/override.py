from graphene import Schema


def override(field, from_: str):
    """
    Decorator to use to override a given type.
    """
    field._override = from_
    return field


def get_override_fields(schema: Schema) -> dict:
    """
    Find all the overridden types from the schema.
    They can be easily distinguished from the other type as
    the `@override` decorator adds a `_override` attribute to them.
    """
    override_fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_override", False):
                override_fields[type_name] = type_.graphene_type
                continue
    return override_fields
