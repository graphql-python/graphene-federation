from pathlib import Path

import pytest
from graphene import Field, ID, ObjectType, String

from graphene_federation import build_schema, key, provides, requires
from tests.util import file_handlers

save_file, open_file = file_handlers(Path(__file__))


def test_key_auto_camelcase_false():
    try:

        @key("identifier")
        @key("valid_email")
        class User(ObjectType):
            identifier = ID()
            email = String(name="valid_email")

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=False)
    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")


def test_key_auto_camelcase_true():
    with pytest.raises(ValueError) as err:

        @key("identifier")
        @key("valid_email")
        class User(ObjectType):
            identifier = ID()
            email = String(name="valid_email")

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=True)

    assert str(err.value) == '@key, field "validEmail" does not exist on type "User"'


def test_key_auto_camelcase_with_auto_case_false():
    try:

        @key("identifier")
        @key("valid_email", auto_case=False)
        class User(ObjectType):
            identifier = ID()
            email = String(name="valid_email")

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=True)
    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")


def test_requires_auto_camelcase_false():
    try:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = requires(String(), fields="employee { corp_email }")

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=False)
    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")


def test_requires_auto_camelcase_true():
    with pytest.raises(ValueError) as err:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = requires(String(), fields="employee { corp_email }")

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=True)

    assert (
        str(err.value)
        == '@requires, field "corpEmail" does not exist on type "Employee"'
    )


def test_requires_auto_camelcase_with_auto_case_false():
    try:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = requires(
                String(), fields="employee { corp_email }", auto_case=False
            )

        class Query(ObjectType):
            user = Field(User)

        _schema = build_schema(query=Query, auto_camelcase=True)

    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")


def test_provides_auto_camelcase_false():
    try:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = String()

        class Query(ObjectType):
            user = provides(Field(User), fields="employee { corp_email }")

        _schema = build_schema(query=Query, auto_camelcase=False)
    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")


def test_provides_auto_camelcase_true():
    with pytest.raises(ValueError) as err:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = String()

        class Query(ObjectType):
            user = provides(Field(User), fields="employee { corp_email }")

        _schema = build_schema(query=Query, auto_camelcase=True)

    assert (
        str(err.value)
        == '@provides, field "corpEmail" does not exist on type "Employee"'
    )


def test_provides_auto_camelcase_with_auto_case_false():
    try:

        class Employee(ObjectType):
            identifier = ID()
            email = String(name="corp_email")

        class User(ObjectType):
            identifier = ID()
            employee = Field(Employee)
            email = String()

        class Query(ObjectType):
            user = provides(
                Field(User), fields="employee { corp_email }", auto_case=False
            )

        _schema = build_schema(query=Query, auto_camelcase=True)

    except Exception as exc:
        pytest.fail(f"Unexpected Error {exc}")
