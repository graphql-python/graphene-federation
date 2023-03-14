import graphene

from graphene_federation import inaccessible, external, provides, key, override

from graphene_federation import build_schema


@key(fields="x")
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = external(graphene.Int(required=True))
    z = inaccessible(graphene.Int(required=True))
    a = provides(graphene.Int(), fields="x")
    b = override(graphene.Int(required=True), from_="h")


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
# {'_service': {'sdl': 'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@external", "@key", "@override", "@provides", "@inaccessible"])\ntype Query {\n  position: Position\n}\n\ntype Position @key(fields: "x") {\n  x: Int!\n  y: Int! @external\n  z: Int! @inaccessible\n  a: Int @provides(fields: "x")\n  b: Int! @override(from: "h")\n}'}}
