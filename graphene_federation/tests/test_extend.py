import pytest

from graphene import ObjectType, ID, String

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
