from pathlib import Path

import pytest
from graphene import Field, ID, ObjectType, String
from graphene import Int
from graphene_directives import DirectiveValidationError

from graphene_federation import LATEST_VERSION, build_schema
from graphene_federation import override
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_chain_requires_failure():
    """
    Check that we can't nest call the override method on a field.
    """
    with pytest.raises(DirectiveValidationError) as err:

        class A(ObjectType):
            something = override(
                override(String(), from_="subgraph-1"), from_="subgraph-2"
            )

    assert "@override is not repeatable" in str(err.value)


def test_override():
    """
    Check that requires can take more than one field as input.
    """

    class Product(ObjectType):
        sku = override(ID(), from_="subgraph-1")
        size = override(Int(), from_="subgraph-2")
        weight = override(Int(), from_="subgraph-3", label="Test label")

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
