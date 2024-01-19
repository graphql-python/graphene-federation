from pathlib import Path

import graphene
import pytest
from graphene import ObjectType
from graphene_directives import DirectiveValidationError

from graphene_federation import LATEST_VERSION, build_schema
from graphene_federation import shareable
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_shareable_interface_failures():
    with pytest.raises(DirectiveValidationError) as err:

        @shareable
        class ReviewInterface(graphene.Interface):
            interfaced_body = graphene.String(required=True)

        @shareable
        class Review(graphene.ObjectType):
            class Meta:
                interfaces = (ReviewInterface,)

            id = shareable(graphene.Int(required=True))
            body = graphene.String(required=True)

        class Query(ObjectType):
            in_stock_count = graphene.Int(required=True)

        build_schema(
            query=Query,
            federation_version=LATEST_VERSION,
            types=(ReviewInterface, Review),
        )

    assert "@shareable cannot be used for ReviewInterface" in str(err.value)


def test_shareable():
    @shareable
    class Position(graphene.ObjectType):
        x = graphene.Int(required=True)
        y = shareable(graphene.Int(required=True))

    class Query(ObjectType):
        in_stock_count = graphene.Int(required=True)

    schema = build_schema(
        query=Query, federation_version=LATEST_VERSION, types=(Position,)
    )

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_shareable_union():
    with pytest.raises(DirectiveValidationError) as err:

        @shareable
        class Human(graphene.ObjectType):
            name = graphene.String()
            born_in = graphene.String()

        @shareable
        class Droid(graphene.ObjectType):
            name = shareable(graphene.String())
            primary_function = graphene.String()

        @shareable
        class Starship(graphene.ObjectType):
            name = graphene.String()
            length = shareable(graphene.Int())

        @shareable
        class SearchResult(graphene.Union):
            class Meta:
                types = (Human, Droid, Starship)

        class Query(ObjectType):
            in_stock_count = graphene.Int(required=True)

        _ = build_schema(
            query=Query, federation_version=LATEST_VERSION, types=(SearchResult,)
        )

    assert "@shareable cannot be used for SearchResult" in str(err.value)
