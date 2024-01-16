from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLDirective

from .v2_0 import shareable_directive as sharable_directive_v2_0
from .v2_1 import get_directives as get_directives_v2_1

shareable_directive = CustomDirective(
    name="shareable",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
    ],
    description="Federation @shareable directive",
    add_definition_to_schema=False,
    is_repeatable=True,  # Changed from v2.1
)


def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_1()
    directives.update(
        {directive.name: directive for directive in [sharable_directive_v2_0]}
    )
    return directives
