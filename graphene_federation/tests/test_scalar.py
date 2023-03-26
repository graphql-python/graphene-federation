from typing import Any

import graphene
from graphene import Scalar, String, ObjectType
from graphql import graphql_sync

from graphene_federation import build_schema, shareable, inaccessible


def test_custom_scalar():
    class AddressScalar(Scalar):
        base = String

        @staticmethod
        def coerce_address(value: Any):
            ...

        serialize = coerce_address
        parse_value = coerce_address

        @staticmethod
        def parse_literal(ast):
            ...

    @shareable
    class TestScalar(graphene.ObjectType):
        test_shareable_scalar = shareable(String(x=AddressScalar()))
        test_inaccessible_scalar = inaccessible(String(x=AddressScalar()))

    class Query(ObjectType):
        test = String(x=AddressScalar())
        test2 = graphene.List(AddressScalar, required=True)

    schema = build_schema(query=Query, enable_federation_2=True, types=(TestScalar,))
    query = """
        query {
            _service {
                sdl
            }
        }
        """
    result = graphql_sync(schema.graphql_schema, query)
    assert (
        result.data["_service"]["sdl"].strip()
        == """extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@inaccessible", "@shareable"])
type TestScalar  @shareable {
  testShareableScalar(x: AddressScalar): String @shareable
  testInaccessibleScalar(x: AddressScalar): String @inaccessible
}

scalar AddressScalar

type Query {
  test(x: AddressScalar): String
  test2: [AddressScalar]!
}"""
    )
