from textwrap import dedent

from graphql import graphql_sync

from graphene import Field, Int, ObjectType, String

from graphene_federation.provides import provides
from graphene_federation.main import build_schema
from graphene_federation.extend import extend
from graphene_federation.external import external
from graphene_federation.utils import clean_schema


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
    expected_result = dedent(
        """
    type Query {
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
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
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
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


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
    expected_result = dedent(
        """
    type Query {
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
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
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
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


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
    expected_result = dedent(
        """
    type Query {
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
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
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
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)
