from pathlib import Path

import graphene
from graphene import ObjectType

from graphene_federation import LATEST_VERSION, build_schema
from graphene_federation import inaccessible, shareable
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_custom_enum():
    @inaccessible
    class Episode(graphene.Enum):
        NEWHOPE = 4
        EMPIRE = 5
        JEDI = 6

    inaccessible(Episode.NEWHOPE)

    @shareable
    class TestCustomEnum(graphene.ObjectType):
        test_shareable_scalar = shareable(Episode())
        test_inaccessible_scalar = inaccessible(Episode())

    class Query(ObjectType):
        test = Episode()
        test2 = graphene.List(TestCustomEnum, required=True)

    schema = build_schema(
        query=Query, federation_version=LATEST_VERSION, types=(TestCustomEnum,)
    )

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
