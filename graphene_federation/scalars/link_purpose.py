from graphql import GraphQLEnumType, GraphQLEnumValue

# Reference: https://www.apollographql.com/docs/federation/subgraph-spec/

link_purpose = GraphQLEnumType(
    name="link__Purpose",
    description="An Enum to clarify the type of directives (security, execution) in the specification",
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
