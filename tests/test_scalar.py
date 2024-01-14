from pathlib import Path
from typing import Any

import graphene
from graphene import ObjectType, String
from graphene import Scalar

from graphene_federation import build_schema
from graphene_federation import inaccessible, shareable
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


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

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
