from pathlib import Path

from graphene import Field, ID, ObjectType, String

from graphene_federation import (
    LATEST_VERSION,
    build_schema,
    extends,
    external,
    key,
    requires,
)
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_similar_field_name():
    """
    Test annotation with fields that have similar names.
    """

    @extends
    @key("id")
    class ChatUser(ObjectType):
        uid = ID()
        identified = ID()
        id = external(ID())
        i_d = ID()
        ID = ID()

    class ChatMessage(ObjectType):
        id = ID(required=True)
        user = Field(ChatUser)

    class ChatQuery(ObjectType):
        message = Field(ChatMessage, id=ID(required=True))

    schema = build_schema(query=ChatQuery, federation_version=LATEST_VERSION)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_camel_case_field_name():
    """
    Test annotation with fields that have camel cases or snake case.
    """

    @key("auto_camel")
    @extends
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_camel_case_field_name_without_auto_camelcase():
    """
    Test annotation with fields that have camel cases or snake case but with the auto_camelcase disabled.
    """

    @extends
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(
        query=Query, auto_camelcase=False, federation_version=LATEST_VERSION
    )

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_annotated_field_also_used_in_filter():
    """
    Test that when a field also used in filter needs to get annotated, it really annotates only the field.
    See issue https://github.com/preply/graphene-federation/issues/50
    """

    @key("id")
    class B(ObjectType):
        id = ID()

    @extends
    class A(ObjectType):
        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


def test_annotate_object_with_meta_name():
    @key("id")
    class B(ObjectType):
        class Meta:
            name = "Potato"

        id = ID()

    @extends
    class A(ObjectType):
        class Meta:
            name = "Banana"

        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
