from graphql import GraphQLEnumType, GraphQLEnumValue

# Reference: https://www.apollographql.com/docs/federation/subgraph-spec/

link_purpose = GraphQLEnumType(
    name="link__Purpose",
    values={
        "SECURITY": GraphQLEnumValue(
            value="SECURITY",
            description="`SECURITY` features provide metadata necessary to securely resolve fields.",
        ),
        "EXECUTION": GraphQLEnumValue(
            value="EXECUTION",
            description="`EXECUTION` features provide metadata necessary for operation execution.",
        ),
    },
)
