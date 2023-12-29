from textwrap import dedent

import graphene
from graphene import ObjectType
from graphql import graphql_sync

from graphene_federation import build_schema, shareable, inaccessible
from graphene_federation.utils import clean_schema


def test_custom_enum():
    class Episode(graphene.Enum):
        NEWHOPE = 4
        EMPIRE = 5
        JEDI = 6

    @shareable
    class TestCustomEnum(graphene.ObjectType):
        test_shareable_scalar = shareable(Episode())
        test_inaccessible_scalar = inaccessible(Episode())

    class Query(ObjectType):
        test = Episode()
        test2 = graphene.List(TestCustomEnum, required=True)

    schema = build_schema(
        query=Query, enable_federation_2=True, types=(TestCustomEnum,)
    )
    query = """
        query {
            _service {
                sdl
            }
        }
        """
    result = graphql_sync(schema.graphql_schema, query)
    expected_result = dedent(
        """
    extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@inaccessible", "@shareable"])
    type TestCustomEnum  @shareable {
      testShareableScalar: Episode @shareable
      testInaccessibleScalar: Episode @inaccessible
    }
    
    enum Episode {
      NEWHOPE
      EMPIRE
      JEDI
    }
    
    type Query {
      test: Episode
      test2: [TestCustomEnum]!
    }
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)
