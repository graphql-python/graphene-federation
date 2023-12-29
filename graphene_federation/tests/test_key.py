import pytest
from textwrap import dedent

from graphql import graphql_sync

from graphene import ObjectType, ID, String, Field

from graphene_federation.entity import key
from graphene_federation.main import build_schema
from graphene_federation.utils import clean_schema


def test_multiple_keys():
    @key("identifier")
    @key("email")
    class User(ObjectType):
        identifier = ID()
        email = String()

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query, enable_federation_2=True)
    expected_result = dedent(
        """
    type Query {
      user: User
      _entities(representations: [_Any!]!): [_Entity]!
      _service: _Service!
    }
    
    type User {
      identifier: ID
      email: String
    }
    
    union _Entity = User
    
    scalar _Any
    
    type _Service {
      sdl: String
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
    extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key"])
    type Query {
      user: User
    }
    
    type User @key(fields: "email") @key(fields: "identifier") {
      identifier: ID
      email: String
    }
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


def test_key_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(AssertionError) as err:

        @key("potato")
        class A(ObjectType):
            id = ID()

    assert 'Field "potato" does not exist on type "A"' == str(err.value)


def test_compound_primary_key():
    class Organization(ObjectType):
        registration_number = ID()

    @key("id organization { registration_number }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query, enable_federation_2=True)
    expected_result = dedent(
        """
    type Query {
      user: User
      _entities(representations: [_Any!]!): [_Entity]!
      _service: _Service!
    }
    
    type User {
      id: ID
      organization: Organization
    }
    
    type Organization {
      registrationNumber: ID
    }
    
    union _Entity = User
    
    scalar _Any
    
    type _Service {
      sdl: String
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
    extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key"])
    type Query {
      user: User
    }
    
    type User @key(fields: "id organization { registrationNumber }") {
      id: ID
      organization: Organization
    }
    
    type Organization {
      registrationNumber: ID
    }
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


def test_compound_primary_key_with_depth():
    class BusinessUnit(ObjectType):
        id = ID()
        name = String()

    class Organization(ObjectType):
        registration_number = ID()
        business_unit = Field(BusinessUnit)

    @key("id organization { business_unit {id name}}")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query, enable_federation_2=True)
    expected_result = dedent(
        """
    type Query {
      user: User
      _entities(representations: [_Any!]!): [_Entity]!
      _service: _Service!
    }
    
    type User {
      id: ID
      organization: Organization
    }
    
    type Organization {
      registrationNumber: ID
      businessUnit: BusinessUnit
    }
    
    type BusinessUnit {
      id: ID
      name: String
    }
    
    union _Entity = User
    
    scalar _Any
    
    type _Service {
      sdl: String
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
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
    expected_result = dedent(
        """
    extend schema @link(url: "https://specs.apollo.dev/federation/v2.0", import: ["@key"])
    type Query {
      user: User
    }
    
    type User @key(fields: "id organization { businessUnit {id name}}") {
      id: ID
      organization: Organization
    }
    
    type Organization {
      registrationNumber: ID
      businessUnit: BusinessUnit
    }
    
    type BusinessUnit {
      id: ID
      name: String
    }
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


def test_invalid_compound_primary_key_failures():
    class BusinessUnit(ObjectType):
        id = ID()
        name = String()

    class Organization(ObjectType):
        registration_number = ID()
        bu = Field(BusinessUnit)

    @key("id name organization { registration_number }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(AssertionError) as err:
        # Field name absent on User ObjectType
        build_schema(query=Query, enable_federation_2=True)

    assert 'Invalid compound key definition for type "User"' == str(err.value)

    @key("id organization { name }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(AssertionError) as err:
        # Presence of invalid field in organization field key
        build_schema(query=Query, enable_federation_2=True)

    assert 'Invalid compound key definition for type "User"' == str(err.value)

    @key("id organization { bu }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(AssertionError) as err:
        # Presence of BusinessUnit in the key without subselection
        build_schema(query=Query, enable_federation_2=True)

    assert 'Invalid compound key definition for type "User"' == str(err.value)

    @key("id organization { bu {name { field }} }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(AssertionError) as err:
        # Presence of subselection for the scalar 'name' field
        build_schema(query=Query, enable_federation_2=True)

    assert 'Invalid compound key definition for type "User"' == str(err.value)
