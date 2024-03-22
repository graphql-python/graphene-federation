import pytest
from graphene import ID, ObjectType, String
from graphene_directives import DirectiveValidationError

from graphene_federation import build_schema, extends, key


def test_extend_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(ValueError) as err:

        @key("potato")
        @extends
        class A(ObjectType):
            id = ID()

        build_schema(types=(A,))

    assert str(err.value) == '@key, field "potato" does not exist on type "A"'


def test_multiple_extend_failure():
    """
    Test that the extend decorator can't be used more than once on a type.
    """
    with pytest.raises(DirectiveValidationError) as err:

        @extends
        @extends
        class A(ObjectType):
            id = ID()
            potato = String()

    assert str(err.value) == "@extends is not repeatable, at: A"
