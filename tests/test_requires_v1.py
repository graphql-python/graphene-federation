from pathlib import Path

import pytest
from graphene import Field, ID, ObjectType, String
from graphene import Int
from graphene_directives import DirectiveValidationError

from graphene_federation import build_schema, key
from graphene_federation import extends, external, requires
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_chain_requires_failure():
    """
    Check that we can't nest call the requires method on a field.
    """
    with pytest.raises(DirectiveValidationError) as err:

        class A(ObjectType):
            id = external(ID())
            something = requires(requires(String(), fields="id"), fields="id3")

    assert "@requires is not repeatable" in str(err.value)


def test_requires_multiple_fields():
    """
    Check that requires can take more than one field as input.
    """

    @key("sku")
    @extends
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields="size weight")

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_requires_multiple_fields_as_list():
    """
    Check that requires can take more than one field as input.
    """

    @key("sku")
    @extends
    class Product(ObjectType):
        sku = external(ID())
        size = external(Int())
        weight = external(Int())
        shipping_estimate = requires(String(), fields=["size", "weight"])

    class Query(ObjectType):
        product = Field(Product)

    schema = build_schema(query=Query)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_requires_with_input():
    """
    Test checking that the issue https://github.com/preply/graphene-federation/pull/47 is resolved.
    """

    @key("id")
    @extends
    class Acme(ObjectType):
        id = external(ID(required=True))
        age = external(Int())
        foo = requires(Field(String, someInput=String()), fields="age")

    class Query(ObjectType):
        acme = Field(Acme)

    schema = build_schema(query=Query)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
