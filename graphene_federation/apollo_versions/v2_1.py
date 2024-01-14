from graphene_directives import CustomDirective, DirectiveLocation
from graphql import (
    GraphQLArgument,
    GraphQLDirective,
    GraphQLNonNull,
    GraphQLString,
)

from .v2_0 import get_directives as get_directives_v2_0

compose_directive = CustomDirective(
    name="composeDirective",
    locations=[
        DirectiveLocation.SCHEMA,
    ],
    args={
        "name": GraphQLArgument(GraphQLNonNull(GraphQLString)),
    },
    description="Federation @composeDirective directive",
    add_definition_to_schema=False,
)


def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_0()
    directives.update({directive.name: directive for directive in [compose_directive]})
    return directives
