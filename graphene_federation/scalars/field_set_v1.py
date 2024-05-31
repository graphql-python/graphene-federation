from graphql import GraphQLScalarType

# Reference: https://www.apollographql.com/docs/federation/subgraph-spec/
_FieldSet = GraphQLScalarType(
    name="_FieldSet",
    description=" ".join(
        (
            "A string-serialized scalar represents a set of fields that's passed to a federated directive,",
            "such as @key, @requires, or @provides",
        )
    ),
)
