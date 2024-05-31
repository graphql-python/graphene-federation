from graphene import Scalar, String


# Reference: https://www.apollographql.com/docs/federation/subgraph-spec/
class _Any(Scalar):
    name = "_Any"
    __typename = String(required=True)
    description = "A JSON serialized used for entity representations"
    specified_by_url = None

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value
