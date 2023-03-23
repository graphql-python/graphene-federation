import graphene
import pytest
from graphene import ObjectType
from graphql import graphql_sync

from .. import shareable, build_schema


@pytest.mark.xfail(
    reason="The @Shareable directive is about indicating when an object field "
    "can be resolved by multiple subgraphs. As interface fields are not "
    "directly resolved (their implementation is), @Shareable is not "
    "meaningful on an interface field and is not allowed (at least since "
    "federation 2.2; earlier versions of federation 2 mistakenly ignored "
    "@Shareable on interface fields)."
)
def test_shareable_interface_failures():
    @shareable
    class ReviewInterface(graphene.Interface):
        interfaced_body = graphene.String(required=True)

    @shareable
    class Review(graphene.ObjectType):
        class Meta:
            interfaces = (ReviewInterface,)

        id = shareable(graphene.Int(required=True))
        body = graphene.String(required=True)

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    build_schema(query=Query, enable_federation_2=True, types=(ReviewInterface, Review))


def test_shareable():
    @shareable
    class Position(graphene.ObjectType):
        x = graphene.Int(required=True)
        y = shareable(graphene.Int(required=True))

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
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@shareable"])
type Position  @shareable {
  x: Int!
  y: Int! @shareable
}

type Query {
  inStockCount: Int!
}""".strip()
    )


def test_shareable_union():
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
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@shareable"])
union SearchResult @shareable  = Human | Droid | Starship

type Human  @shareable {
  name: String
  bornIn: String
}

type Droid  @shareable {
  name: String @shareable
  primaryFunction: String
}

type Starship  @shareable {
  name: String
  length: Int @shareable
}

type Query {
  inStockCount: Int!
}""".strip()
    )
