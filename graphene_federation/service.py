from graphene import Field, ObjectType, String
from graphene_directives.schema import Schema


def get_sdl(schema) -> str:
    """
    Add all needed decorators to the string representation of the schema.
    """

    string_schema = str(schema)
    return string_schema.strip()


def get_service_query(schema: Schema):
    """
    Gets the Service Query for federation
    """
    sdl_str = get_sdl(schema)

    class _Service(ObjectType):
        sdl = String()

        def resolve_sdl(self, _) -> str:  # noqa
            return sdl_str

    class ServiceQuery(ObjectType):
        _service = Field(_Service, name="_service", required=True)

        def resolve__service(self, info) -> _Service:  # noqa
            return _Service()

    return ServiceQuery
