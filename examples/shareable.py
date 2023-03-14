import graphene
from graphene_federation.shareable import shareable

from graphene_federation import build_schema


@shareable
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = shareable(graphene.Int(required=True))


@shareable
class ReviewInterface(graphene.Interface):
    interfaced_body = graphene.String(required=True)


@shareable
class Review(graphene.ObjectType):
    class Meta:
        interfaces = (ReviewInterface,)

    id = shareable(graphene.Int(required=True))
    body = graphene.String(required=True)


@shareable
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@shareable
class Droid(graphene.ObjectType):
    name = shareable(graphene.String())
    primary_function = graphene.String()


@shareable
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = shareable(graphene.Int())


@shareable
class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


class Query(graphene.ObjectType):
    position = graphene.Field(Position)


schema = build_schema(Query, enable_federation_2=True, types=(ReviewInterface, SearchResult, Review))

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
