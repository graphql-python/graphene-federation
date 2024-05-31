from typing import Any

from graphql import (
    GraphQLError,
    GraphQLScalarType,
    StringValueNode,
    ValueNode,
    print_ast,
)
from graphql.pyutils import inspect


def _serialize_string(output_value: Any) -> str:
    if isinstance(output_value, str):
        return output_value
    # do not serialize builtin types as strings, but allow serialization of custom
    # types via their `__str__` method
    if type(output_value).__module__ == "builtins":
        raise GraphQLError(
            "federation__Policy cannot represent value: " + inspect(output_value)
        )

    return str(output_value)


def _coerce_string(input_value: Any) -> str:
    if not isinstance(input_value, str):
        raise GraphQLError(
            "federation__Policy cannot represent a non string value: "
            + inspect(input_value)
        )
    return input_value


def _parse_string_literal(value_node: ValueNode, _variables: Any = None) -> str:
    """Parse a string value node in the AST."""
    if not isinstance(value_node, StringValueNode):
        raise GraphQLError(
            "federation__Policy cannot represent a non string value: "
            + print_ast(value_node),
            value_node,
        )
    return value_node.value


# Reference: https://www.apollographql.com/docs/federation/subgraph-spec/
FederationPolicy = GraphQLScalarType(
    name="federation__Policy",
    description="This string-serialized scalar represents an authorization policy.",
    serialize=_serialize_string,
    parse_value=_coerce_string,
    parse_literal=_parse_string_literal,
)
