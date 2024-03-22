import graphene

from graphene_federation import (
    LATEST_VERSION,
    inaccessible,
    external,
    provides,
    key,
    override,
)

from graphene_federation import build_schema


@key(fields="x")
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = external(graphene.Int(required=True))
    z = inaccessible(graphene.Int(required=True))
    a = provides(graphene.Int(), fields="x")
    b = override(graphene.Int(required=True), from_="h")


@inaccessible
class ReviewInterface(graphene.Interface):
    interfaced_body = graphene.String(required=True)


@inaccessible
class Review(graphene.ObjectType):
    class Meta:
        interfaces = (ReviewInterface,)

    id = graphene.Int(required=True)
    body = graphene.String(required=True)


@inaccessible
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@inaccessible
class Droid(graphene.ObjectType):
    name = graphene.String()
    primary_function = graphene.String()


@inaccessible
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = graphene.Int()


@inaccessible
class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


class Query(graphene.ObjectType):
    position = graphene.Field(Position)


schema = build_schema(
    Query,
    federation_version=LATEST_VERSION,
    types=(ReviewInterface, SearchResult, Review),
)

query = """
    query getSDL {
      _service {
         sdl
      }
    }
"""
result = schema.execute(query)
print(result.data)
# {'_service': {'sdl': 'extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@external", "@key", "@override", "@provides", "@inaccessible"])\ntype Query {\n  position: Position\n}\n\ntype Position @key(fields: "x") {\n  x: Int!\n  y: Int! @external\n  z: Int! @inaccessible\n  a: Int @provides(fields: "x")\n  b: Int! @override(from: "h")\n}'}}
