from typing import Any

from graphene import Enum, InputObjectType, Interface, ObjectType, Scalar, Union


def is_non_field(field: Any):
    try:
        if (
            issubclass(field, ObjectType)
            or issubclass(field, Interface)
            or issubclass(field, InputObjectType)
            or issubclass(field, Enum)
            or issubclass(field, Union)
            or issubclass(field, Scalar)
        ):
            return True
        else:
            return False
    except TypeError:
        return False
