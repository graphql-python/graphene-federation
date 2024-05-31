from pathlib import Path

from graphene import Field, ObjectType, String
from graphene import Int

from graphene_federation import LATEST_VERSION, build_schema, extends, key
from graphene_federation import external, provides
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_provides():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @key("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_provides_multiple_fields():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @key("sku")
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields="name weight")
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_provides_multiple_fields_as_list():
    """
    https://www.apollographql.com/docs/federation/entities/#resolving-another-services-field-advanced
    """

    @key("sku")
    @extends
    class Product(ObjectType):
        sku = external(String(required=True))
        name = external(String())
        weight = external(Int())

    class InStockCount(ObjectType):
        product = provides(Field(Product, required=True), fields=["name", "weight"])
        quantity = Int(required=True)

    class Query(ObjectType):
        in_stock_count = Field(InStockCount)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
