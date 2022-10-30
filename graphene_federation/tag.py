from graphene import Schema


def tag(field, name: str):
    """
    Decorator to use to override a given type.
    """
    field._tag = name
    return field


def get_tagged_fields(schema: Schema) -> dict:
    """
    Find all the tagged types from the schema.
    They can be easily distinguished from the other type as
    the `@tag` decorator adds a `_tag` attribute to them.
    """
    tagged_fields = {}
    for type_name, type_ in schema.graphql_schema.type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue
        for field in list(type_.graphene_type.__dict__):
            if getattr(getattr(type_.graphene_type, field), "_tag", False):
                tagged_fields[type_name] = type_.graphene_type
                continue
    return tagged_fields
