from pathlib import Path

import pytest
from graphene import Field, ID, ObjectType, String

from graphene_federation import FederationVersion, build_schema, key
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_multiple_keys():
    @key("identifier")
    @key("email")
    class User(ObjectType):
        identifier = ID()
        email = String()

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query, federation_version=FederationVersion.VERSION_1_0)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_key_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(ValueError) as err:

        @key("potato")
        class A(ObjectType):
            id = ID()

        _ = build_schema(types=(A,), federation_version=FederationVersion.VERSION_1_0)

    assert '@key, field "potato" does not exist on type "A"' == str(err.value)
