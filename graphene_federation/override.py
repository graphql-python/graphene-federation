def override(field, _from: str):
    """
    Decorator to use to override a given type.
    """
    field._override = _from
    return field
