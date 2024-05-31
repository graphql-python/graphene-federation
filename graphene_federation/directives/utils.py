import inspect
from typing import Any


def is_non_field(graphene_type: Any):
    """Check of a given graphene_type is a non-field"""
    return inspect.isclass(graphene_type)
