from typing import Optional

from graphene_directives import CustomDirective, DirectiveLocation, SchemaDirective
from graphql import (
    GraphQLArgument,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)

from ..scalars import link_import, link_purpose

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
    return SchemaDirective(
        target_directive=_link_directive,
        arguments={"url": url, "as": as_, "for": for_, "import": import_},
    )
