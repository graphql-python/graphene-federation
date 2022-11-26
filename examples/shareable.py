import graphene
from graphene_federation.shareable import shareable

from graphene_federation import build_schema


@shareable
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = shareable(graphene.Int(required=True))


class Query(graphene.ObjectType):
    position = graphene.Field(Position)


schema = build_schema(Query, enable_federation_2=True)

query = '''
    query getSDL {
      _service {
         sdl
      }
    }
'''
result = schema.execute(query)
print(result.data)
# {'_service': {'sdl': 'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@shareable"])\ntype Query {\n  position: Position\n}\n\ntype Position  @shareable {\n  x: Int!\n  y: Int! @shareable\n}'}}
