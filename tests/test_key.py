from pathlib import Path

import pytest
from graphene import Field, ID, ObjectType, String

from graphene_federation import build_schema, key
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

    schema = build_schema(query=Query, enable_federation_2=True)

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

        build_schema(types=(A,), enable_federation_2=True)

    assert '@key, field "potato" does not exist on type "A"' == str(err.value)


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

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


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
    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)


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

    with pytest.raises(ValueError) as err:
        # Field name absent on User ObjectType
        build_schema(query=Query, enable_federation_2=True)

    assert '@key, field "name" does not exist on type "User"' == str(err.value)

    @key("id organization { name }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(ValueError) as err:
        # Presence of invalid field in organization field key
        build_schema(query=Query, enable_federation_2=True)

    assert '@key, field "name" does not exist on type "Organization"' == str(err.value)

    @key("id organization { bu }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(ValueError) as err:
        # Presence of BusinessUnit in the key without subselection
        build_schema(query=Query, enable_federation_2=True)

    assert '@key, type Organization, field "bu" needs sub selections.' == str(err.value)

    @key("id organization { bu {name { field }} }")
    class User(ObjectType):
        id = ID()
        organization = Field(Organization)

    class Query(ObjectType):
        user = Field(User)

    with pytest.raises(ValueError) as err:
        # Presence of subselection for the scalar 'name' field
        build_schema(query=Query, enable_federation_2=True)

    assert '@key, type BusinessUnit, field "name" cannot have sub selections.' == str(
        err.value
    )
