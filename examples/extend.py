import graphene

from graphene_federation import build_schema, extends, external, key


@key("id")
@extends
class Message(graphene.ObjectType):
    id = external(graphene.Int(required=True))

    def resolve_id(self, **kwargs):
        return 1


class Query(graphene.ObjectType):
    message = graphene.Field(Message)

    def resolve_file(self, **kwargs):
        return None  # no direct access


schema = build_schema(Query)

query = """
    query getSDL {
      _service {
         sdl
      }
    }
"""
result = schema.execute(query)
print(result.data)
# {'sdl': 'type Query {\n  message: Message\n}\n\n type Message  @key(fields: "id") @extends {\n  id: Int! @external\n}'}}
