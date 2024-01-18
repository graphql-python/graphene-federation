from typing import Optional

from graphene_directives import CustomDirective, DirectiveLocation, SchemaDirective
from graphql import (
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_federation.scalars import link_import, link_purpose

_link_directive = CustomDirective(
    name="link",
    locations=[
        DirectiveLocation.SCHEMA,
    ],
    args={
        "url": GraphQLArgument(GraphQLNonNull(GraphQLString)),
        "as": GraphQLArgument(GraphQLString),
        "for": GraphQLArgument(link_purpose),
        "import": GraphQLArgument(GraphQLList(link_import)),
    },
    description="Federation @link directive",
    add_definition_to_schema=False,
    is_repeatable=True,
)


def link_directive(
    url: str,
    as_: Optional[str] = None,
    for_: Optional[str] = None,
    import_: Optional[list[str]] = None,
) -> SchemaDirective:
    """
    It's used to link types and fields from external subgraphs, creating a unified GraphQL schema
    across multiple services

    Use this in the `schema_directives` argument of `build_schema`

    It is not recommended to use this directive directly, instead use the ComposableDirective class to build
    a custom directive. It will automatically add the compose and link directive to schema

    Also, the apollo directives such as @key, @external, ... are automatically added to the schema via the link directive

    Reference: https://www.apollographql.com/docs/federation/federated-types/federated-directives/
    """
    return SchemaDirective(
        target_directive=_link_directive,
        arguments={"url": url, "as": as_, "for": for_, "import": import_},
    )
