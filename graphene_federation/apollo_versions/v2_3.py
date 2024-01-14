from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLDirective

from .v2_2 import get_directives as get_directives_v2_2

interface_object_directive = CustomDirective(
    name="interfaceObject",
    locations=[
        DirectiveLocation.OBJECT,
    ],
    description="Federation @interfaceObject directive",
    add_definition_to_schema=False,
    is_repeatable=True,
)


def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_2()
    directives.update(
        {directive.name: directive for directive in [interface_object_directive]}
    )
    return directives
