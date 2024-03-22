from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLList, GraphQLNonNull

from .v2_4 import get_directives as get_directives_v2_4
from graphene_federation.scalars import FederationScope

authenticated_directive = CustomDirective(
    name="authenticated",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.SCALAR,
        DirectiveLocation.ENUM,
    ],
    description="Federation @authenticated directive",
    add_definition_to_schema=False,
)

requires_scope_directive = CustomDirective(
    name="requiresScopes",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.SCALAR,
        DirectiveLocation.ENUM,
    ],
    args={
        "scopes": GraphQLArgument(
            GraphQLNonNull(
                GraphQLList(
                    GraphQLNonNull(GraphQLList(GraphQLNonNull(FederationScope)))
                )
            )
        ),
    },
    description="Federation @requiresScopes directive",
    add_definition_to_schema=False,
)


# No Change, Added Subscription Support
def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_4()
    directives.update(
        {
            directive.name: directive
            for directive in [authenticated_directive, requires_scope_directive]
        }
    )
    return directives
