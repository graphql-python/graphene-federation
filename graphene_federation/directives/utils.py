import inspect
from typing import Any


def is_non_field(field: Any):
    return inspect.isclass(field)
