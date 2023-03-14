from graphql import graphql_sync

from graphene import Field, Int, ObjectType, String

from ..provides import provides
from ..main import build_schema
from ..extend import extend
from ..external import external


def test_provides():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

scalar _Any

type _Service {
  sdl: String
}"""
    )
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
        == """
type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name")
  quantity: Int!
}

extend type Product @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}
""".strip()
    )


def test_provides_multiple_fields():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name weight")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

scalar _Any

type _Service {
  sdl: String
}"""
    )
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
        == """
type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}
""".strip()
    )


def test_provides_multiple_fields_as_list():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    @provides
    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields=["name", "weight"])
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  inStockCount: InStockCount
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type InStockCount {
  product: Product!
  quantity: Int!
}

type Product {
  sku: String!
  name: String
  weight: Int
}

union _Entity = Product

scalar _Any

type _Service {
  sdl: String
}"""
    )
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
        == """
type Query {
  inStockCount: InStockCount
}

type InStockCount  {
  product: Product! @provides(fields: "name weight")
  quantity: Int!
}

extend type Product @key(fields: "sku") {
  sku: String! @external
  name: String @external
  weight: Int @external
}
""".strip()
    )
