from pathlib import Path

import graphene
from graphene import ObjectType

from graphene_federation import LATEST_VERSION, build_schema, inaccessible
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_inaccessible_interface():
    @inaccessible
    class ReviewInterface(graphene.Interface):
        interfaced_body = graphene.String(required=True)

    @inaccessible
    class Review(graphene.ObjectType):
        class Meta:
            interfaces = (ReviewInterface,)

        id = inaccessible(graphene.Int(required=True))
        body = graphene.String(required=True)

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    build_schema(
        query=Query, federation_version=LATEST_VERSION, types=(ReviewInterface, Review)
    )


def test_inaccessible():
    @inaccessible
    class Position(graphene.ObjectType):
        x = graphene.Int(required=True)
        y = inaccessible(graphene.Int(required=True))

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    schema = build_schema(
        query=Query, federation_version=LATEST_VERSION, types=(Position,)
    )

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_inaccessible_union():
    @inaccessible
    class Human(graphene.ObjectType):
        name = graphene.String()
        born_in = graphene.String()

    @inaccessible
    class Droid(graphene.ObjectType):
        name = inaccessible(graphene.String())
        primary_function = graphene.String()

    @inaccessible
    class Starship(graphene.ObjectType):
        name = graphene.String()
        length = inaccessible(graphene.Int())

    @inaccessible
    class SearchResult(graphene.Union):
        class Meta:
            types = (Human, Droid, Starship)

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    schema = build_schema(
        query=Query, federation_version=LATEST_VERSION, types=(SearchResult,)
    )

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
