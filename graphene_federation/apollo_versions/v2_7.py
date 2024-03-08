from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLNonNull, GraphQLString

from .v2_6 import get_directives as get_directives_v2_6

override_directive = CustomDirective(
    name="override",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    args={
        "from": GraphQLArgument(GraphQLNonNull(GraphQLString)),
        "label": GraphQLArgument(GraphQLString),
    },
    description="Federation @override directive",
    add_definition_to_schema=False,
)


# @override Change, Added label argument
def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_6()
    directives.update({directive.name: directive for directive in [override_directive]})
    return directives
