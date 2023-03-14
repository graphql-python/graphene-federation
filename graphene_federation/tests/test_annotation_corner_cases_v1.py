import pytest

from graphql import graphql_sync

from graphene import ObjectType, ID, String, Field

from ..entity import key
from ..extend import extend
from ..external import external
from ..requires import requires
from ..main import build_schema


def test_similar_field_name():
    """
    Test annotation with fields that have similar names.
    """

    @extend("id")
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

    chat_schema = build_schema(query=ChatQuery)
    assert (
        str(chat_schema).strip()
        == """schema {
  query: ChatQuery
}

type ChatQuery {
  message(id: ID!): ChatMessage
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type ChatMessage {
  id: ID!
  user: ChatUser
}

type ChatUser {
  uid: ID
  identified: ID
  id: ID
  iD: ID
  ID: ID
}

union _Entity = ChatUser

scalar _Any

type _Service {
  sdl: String
}"""
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(chat_schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """
type ChatQuery {
  message(id: ID!): ChatMessage
}

type ChatMessage {
  id: ID!
  user: ChatUser
}

extend type ChatUser @key(fields: "id") {
  uid: ID
  identified: ID
  id: ID @external
  iD: ID
  ID: ID
}
""".strip()
    )


def test_camel_case_field_name():
    """
    Test annotation with fields that have camel cases or snake case.
    """

    @extend("auto_camel")
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  camel: Camel
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Camel {
  autoCamel: String
  forcedCamel: String
  aSnake: String
  aCamel: String
}

union _Entity = Camel

scalar _Any

type _Service {
  sdl: String
}"""
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """
type Query {
  camel: Camel
}

extend type Camel @key(fields: "autoCamel") {
  autoCamel: String @external
  forcedCamel: String @requires(fields: "autoCamel")
  aSnake: String
  aCamel: String
}
""".strip()
    )


def test_camel_case_field_name_without_auto_camelcase():
    """
    Test annotation with fields that have camel cases or snake case but with the auto_camelcase disabled.
    """

    @extend("auto_camel")
    class Camel(ObjectType):
        auto_camel = external(String())
        forcedCamel = requires(String(), fields="auto_camel")
        a_snake = String()
        aCamel = String()

    class Query(ObjectType):
        camel = Field(Camel)

    schema = build_schema(query=Query, auto_camelcase=False)
    assert (
        str(schema).strip()
        == """type Query {
  camel: Camel
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Camel {
  auto_camel: String
  forcedCamel: String
  a_snake: String
  aCamel: String
}

union _Entity = Camel

scalar _Any

type _Service {
  sdl: String
}"""
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """
type Query {
  camel: Camel
}

extend type Camel @key(fields: "auto_camel") {
  auto_camel: String @external
  forcedCamel: String @requires(fields: "auto_camel")
  a_snake: String
  aCamel: String
}
""".strip()
    )


def test_annotated_field_also_used_in_filter():
    """
    Test that when a field also used in filter needs to get annotated, it really annotates only the field.
    See issue https://github.com/preply/graphene-federation/issues/50
    """

    @key("id")
    class B(ObjectType):
        id = ID()

    @extend("id")
    class A(ObjectType):
        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  a: A
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type A {
  id: ID
  b(id: ID): B
}

type B {
  id: ID
}

union _Entity = A | B

scalar _Any

type _Service {
  sdl: String
}"""
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """
type Query {
  a: A
}

extend type A @key(fields: "id") {
  id: ID @external
  b(id: ID): B
}

type B @key(fields: "id") {
  id: ID
}
""".strip()
    )


def test_annotate_object_with_meta_name():
    @key("id")
    class B(ObjectType):
        class Meta:
            name = "Potato"

        id = ID()

    @extend("id")
    class A(ObjectType):
        class Meta:
            name = "Banana"

        id = external(ID())
        b = Field(B, id=ID())

    class Query(ObjectType):
        a = Field(A)

    schema = build_schema(query=Query)
    assert (
        str(schema).strip()
        == """type Query {
  a: Banana
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type Banana {
  id: ID
  b(id: ID): Potato
}

type Potato {
  id: ID
}

union _Entity = Banana | Potato

scalar _Any

type _Service {
  sdl: String
}"""
    )
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    assert (
        result.data["_service"]["sdl"].strip()
        == """
type Query {
  a: Banana
}

extend type Banana @key(fields: "id") {
  id: ID @external
  b(id: ID): Potato
}

type Potato @key(fields: "id") {
  id: ID
}
""".strip()
    )
