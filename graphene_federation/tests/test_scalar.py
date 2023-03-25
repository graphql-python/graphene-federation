from typing import Any

from graphene import Scalar, String, ObjectType

from graphene_federation import build_schema


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

    class Query(ObjectType):
        test = String(x=AddressScalar())

    build_schema(query=Query, enable_federation_2=True)
