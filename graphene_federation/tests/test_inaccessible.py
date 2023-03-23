import graphene
from graphene import ObjectType
from graphql import graphql_sync

from .. import inaccessible, build_schema


def test_inaccessible_interface():
    @inaccessible
    class ReviewInterface(graphene.Interface):
        interfaced_body = graphene.String(required=True)

    @inaccessible
    class Review(graphene.ObjectType):
        class Meta:
            interfaces = (ReviewInterface,)

        id = inaccessible(graphene.Int(required=True))
        body = graphene.String(required=True)

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    build_schema(query=Query, enable_federation_2=True, types=(ReviewInterface, Review))


def test_inaccessible():
    @inaccessible
    class Position(graphene.ObjectType):
        x = graphene.Int(required=True)
        y = inaccessible(graphene.Int(required=True))

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    schema = build_schema(query=Query, enable_federation_2=True, types=(Position,))
    # Check the federation service schema definition language
    query = """
        query {
            _service {
                sdl
            }
        }
        """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@inaccessible"])
type Position  @inaccessible {
  x: Int!
  y: Int! @inaccessible
}

type Query {
  inStockCount: Int!
}""".strip()
    )


def test_inaccessible_union():
    @inaccessible
    class Human(graphene.ObjectType):
        name = graphene.String()
        born_in = graphene.String()

    @inaccessible
    class Droid(graphene.ObjectType):
        name = inaccessible(graphene.String())
        primary_function = graphene.String()

    @inaccessible
    class Starship(graphene.ObjectType):
        name = graphene.String()
        length = inaccessible(graphene.Int())

    @inaccessible
    class SearchResult(graphene.Union):
        class Meta:
            types = (Human, Droid, Starship)

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    schema = build_schema(query=Query, enable_federation_2=True, types=(SearchResult,))
    # Check the federation service schema definition language
    query = """
        query {
            _service {
                sdl
            }
        }
        """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@inaccessible"])
union SearchResult @inaccessible  = Human | Droid | Starship

type Human  @inaccessible {
  name: String
  bornIn: String
}

type Droid  @inaccessible {
  name: String @inaccessible
  primaryFunction: String
}

type Starship  @inaccessible {
  name: String
  length: Int @inaccessible
}

type Query {
  inStockCount: Int!
}""".strip()
    )
