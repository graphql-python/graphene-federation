import pytest

from graphene import ObjectType, ID, String, Field
from graphql import graphql_sync

from graphene_federation import build_schema, external, shareable

from ..extend import extend


def test_extend_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(AssertionError) as err:

        @extend("potato")
        class A(ObjectType):
            id = ID()

    assert 'Field "potato" does not exist on type "A"' == str(err.value)


def test_multiple_extend_failure():
    """
    Test that the extend decorator can't be used more than once on a type.
    """
    with pytest.raises(AssertionError) as err:

        @extend("id")
        @extend("potato")
        class A(ObjectType):
            id = ID()
            potato = String()

    assert "Can't extend type which is already extended or has @key" == str(err.value)


def test_extend_with_description_failure():
    """
    Test that adding a description to an extended type raises an error.
    """
    with pytest.raises(AssertionError) as err:

        @extend("id")
        class A(ObjectType):
            class Meta:
                description = "This is an object from here."

            id = ID()

    assert (
        'Type "A" has a non empty description and it is also marked with extend.\nThey are mutually exclusive.'
        in str(err.value)
    )


def test_extend_with_compound_primary_keys():
    @shareable
    class Organization(ObjectType):
        id = ID()

    @extend(fields="id organization {id }")
    class User(ObjectType):
        id = external(ID())
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query, enable_federation_2=True)
    assert (
        str(schema).strip()
        == """type Query {
  user: User
  _entities(representations: [_Any!]!): [_Entity]!
  _service: _Service!
}

type User {
  id: ID
  organization: Organization
}

type Organization {
  id: ID
}

union _Entity = User

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
extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@extends", "@external", "@key", "@shareable"])
type Query {
  user: User
}

extend type User @key(fields: "id organization {id }") {
  id: ID @external
  organization: Organization
}

type Organization  @shareable {
  id: ID
}
""".strip()
    )
