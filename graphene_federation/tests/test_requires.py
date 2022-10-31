import pytest

from graphql import graphql_sync

from graphene import Field, ID, Int, ObjectType, String

from .. import external, requires
from ..extend import extend
from ..main import build_schema


def test_chain_requires_failure():
    """
    Check that we can't nest call the requires method on a field.
    """
    with pytest.raises(AssertionError) as err:

        @extend("id")
        class A(ObjectType):
            id = external(ID())
            something = requires(requires(String(), fields="id"), fields="id")

    assert "Can't chain `requires()` method calls on one field." == str(err.value)


def test_requires_multiple_fields():
    """
    Check that requires can take more than one field as input.
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields="size weight")

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query, enable_federation_2=True)
    assert (
        str(schema).strip()
        == """type Query {
  product: Product
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
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
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@extends", "@external", "@key", "@requires"])
type Query {
  product: Product
}

extend type Product @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}
""".strip()
    )


def test_requires_multiple_fields_as_list():
    """
    Check that requires can take more than one field as input.
    """

    @extend("sku")
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields=["size", "weight"])

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query, enable_federation_2=True)
    assert (
        str(schema).strip()
        == """type Query {
  product: Product
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Product {
  sku: ID
  size: Int
  weight: Int
  shippingEstimate: String
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
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@extends", "@external", "@key", "@requires"])
type Query {
  product: Product
}

extend type Product @key(fields: "sku") {
  sku: ID @external
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}
""".strip()
    )


def test_requires_with_input():
    """
    Test checking that the issue https://github.com/preply/graphene-federation/pull/47 is resolved.
    """

    @extend("id")
    class Acme(ObjectType):
        id = external(ID(required=True))
        age = external(Int())
        foo = requires(Field(String, someInput=String()), fields="age")

    class Query(ObjectType):
        acme = Field(Acme)

    schema = build_schema(query=Query, enable_federation_2=True)
    assert (
        str(schema).strip()
        == """type Query {
  acme: Acme
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Acme {
  id: ID!
  age: Int
  foo(someInput: String): String
}

union _Entity = Acme

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
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@extends", "@external", "@key", "@requires"])
type Query {
  acme: Acme
}

extend type Acme @key(fields: "id") {
  id: ID! @external
  age: Int @external
  foo(someInput: String): String @requires(fields: "age")
}
""".strip()
    )
